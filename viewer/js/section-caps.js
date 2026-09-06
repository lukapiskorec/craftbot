// Section caps: the cross-section a clipping plane cuts out of the model, as
// flat triangles lying on that plane. Filling the hole turns a clipped model
// from a hollow shell into a section drawing.
//
// Every member in these models is a box or a convex prism (the experiments'
// separating-axis overlap check relies on it; 43 789 of the 43 881 exported
// mesh elements are convex), so one element cuts to one convex polygon:
// collect the points where the plane crosses the element's edges, order them
// by angle around their centroid, clip that polygon by the other active
// planes and fan-triangulate it.
//
// A plane is [nx, ny, nz, c] and keeps the half where n . p + c >= 0 - the
// same convention as THREE.Plane. Pure geometry, no DOM and no three.js:
// unit-tested with `node --test viewer/test/*.test.mjs`.

// Unit cube of the box instances (BoxGeometry(2, 2, 2)), also used by scene.js
// for the baked edge lines.
export const CUBE_CORNERS = [
  [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1],
  [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1],
];
export const CUBE_EDGES = [
  [0, 1], [1, 2], [2, 3], [3, 0],
  [4, 5], [5, 6], [6, 7], [7, 4],
  [0, 4], [1, 5], [2, 6], [3, 7],
];

const MERGE = 1e-5; // metres: points closer than this are the same corner

const dist = (pl, x, y, z) => pl[0] * x + pl[1] * y + pl[2] * z + pl[3];

// Scratch, reused across elements: 8 box corners and one distance per vertex
const _corners = new Float64Array(24);
let _dist = new Float64Array(256);

function fitDist(n) {
  if (_dist.length < n) _dist = new Float64Array(n * 2);
  return _dist;
}

// Crossing point of the plane with segment (a, b), appended to `pts` as x,y,z
function crossEdge(v, d, a, b, pts) {
  const da = d[a], db = d[b];
  if ((da > 0 && db > 0) || (da < 0 && db < 0)) return;
  if (da === db) return; // segment lies in the plane; its ends come in via the neighbouring edges
  const t = da / (da - db);
  if (t < 0 || t > 1) return;
  const i = a * 3, j = b * 3;
  pts.push(v[i] + (v[j] - v[i]) * t,
    v[i + 1] + (v[j + 1] - v[i + 1]) * t,
    v[i + 2] + (v[j + 2] - v[i + 2]) * t);
}

// Where the plane crosses one box instance (column-major 4x4 at matrices[b*16])
export function boxCrossings(matrices, b, plane, pts) {
  const k = b * 16;
  const d = fitDist(8);
  for (let i = 0; i < 8; i++) {
    const [cx, cy, cz] = CUBE_CORNERS[i];
    const x = matrices[k] * cx + matrices[k + 4] * cy + matrices[k + 8] * cz + matrices[k + 12];
    const y = matrices[k + 1] * cx + matrices[k + 5] * cy + matrices[k + 9] * cz + matrices[k + 13];
    const z = matrices[k + 2] * cx + matrices[k + 6] * cy + matrices[k + 10] * cz + matrices[k + 14];
    _corners[i * 3] = x; _corners[i * 3 + 1] = y; _corners[i * 3 + 2] = z;
    d[i] = dist(plane, x, y, z);
  }
  for (const [a, c] of CUBE_EDGES) crossEdge(_corners, d, a, c, pts);
}

// Where the plane crosses a triangulated element. Shared triangle edges are
// walked twice; the duplicate points drop out when the polygon is ordered.
export function meshCrossings(verts, index, plane, pts) {
  const n = verts.length / 3;
  const d = fitDist(n);
  for (let i = 0; i < n; i++) d[i] = dist(plane, verts[i * 3], verts[i * 3 + 1], verts[i * 3 + 2]);
  for (let i = 0; i < index.length; i += 3) {
    const a = index[i], b = index[i + 1], c = index[i + 2];
    crossEdge(verts, d, a, b, pts);
    crossEdge(verts, d, b, c, pts);
    crossEdge(verts, d, c, a, pts);
  }
}

// Two unit vectors spanning the plane
function basis(plane) {
  const [nx, ny, nz] = plane;
  const ax = Math.abs(nx) < 0.9 ? 1 : 0; // an axis that is not parallel to n
  const ay = 1 - ax;
  let ux = -nz * ay, uy = nz * ax, uz = nx * ay - ny * ax; // u = n x axis
  const l = Math.hypot(ux, uy, uz) || 1;
  ux /= l; uy /= l; uz /= l;
  return [ux, uy, uz, ny * uz - nz * uy, nz * ux - nx * uz, nx * uy - ny * ux];
}

// Sutherland-Hodgman: the part of a convex polygon on the kept side of `pl`
function clipPolygon(poly, pl) {
  const n = poly.length / 3;
  const out = [];
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const ax = poly[i * 3], ay = poly[i * 3 + 1], az = poly[i * 3 + 2];
    const bx = poly[j * 3], by = poly[j * 3 + 1], bz = poly[j * 3 + 2];
    const da = dist(pl, ax, ay, az), db = dist(pl, bx, by, bz);
    if (da >= 0) out.push(ax, ay, az);
    if ((da < 0) !== (db < 0)) {
      const t = da / (da - db);
      out.push(ax + (bx - ax) * t, ay + (by - ay) * t, az + (bz - az) * t);
    }
  }
  return out;
}

// Crossing points -> the convex polygon they bound, ordered around the plane
export function orderPolygon(pts, plane) {
  const n = pts.length / 3;
  if (n < 3) return [];
  let cx = 0, cy = 0, cz = 0;
  for (let i = 0; i < n; i++) { cx += pts[i * 3]; cy += pts[i * 3 + 1]; cz += pts[i * 3 + 2]; }
  cx /= n; cy /= n; cz /= n;
  const [ux, uy, uz, vx, vy, vz] = basis(plane);
  const angle = new Float64Array(n);
  const order = [];
  for (let i = 0; i < n; i++) {
    const dx = pts[i * 3] - cx, dy = pts[i * 3 + 1] - cy, dz = pts[i * 3 + 2] - cz;
    angle[i] = Math.atan2(dx * vx + dy * vy + dz * vz, dx * ux + dy * uy + dz * uz);
    order.push(i);
  }
  order.sort((a, b) => angle[a] - angle[b]);
  const poly = [];
  for (const i of order) {
    const x = pts[i * 3], y = pts[i * 3 + 1], z = pts[i * 3 + 2];
    const m = poly.length;
    if (m && Math.abs(poly[m - 3] - x) < MERGE && Math.abs(poly[m - 2] - y) < MERGE
      && Math.abs(poly[m - 1] - z) < MERGE) continue;
    poly.push(x, y, z);
  }
  const m = poly.length;
  if (m >= 9 && Math.abs(poly[m - 3] - poly[0]) < MERGE && Math.abs(poly[m - 2] - poly[1]) < MERGE
    && Math.abs(poly[m - 1] - poly[2]) < MERGE) poly.length = m - 3;
  return poly;
}

// Does `plane` pass through the element's bounding sphere?
function crosses(model, eid, plane) {
  const i = eid * 3;
  const r = 0.5 * Math.hypot(model.dims[i], model.dims[i + 1], model.dims[i + 2]);
  return Math.abs(dist(plane, model.centers[i], model.centers[i + 1], model.centers[i + 2])) <= r;
}

// Cut faces of the whole model at every plane, as flat xyz triangles.
// isVisible(elementId) drops hidden layers.
export function buildCaps(model, planes, isVisible = null) {
  const out = [];
  const pts = [];
  for (let p = 0; p < planes.length; p++) {
    const plane = planes[p];
    const others = planes.filter((_, i) => i !== p);
    const emit = () => {
      let poly = orderPolygon(pts, plane);
      for (const pl of others) {
        if (poly.length < 9) break;
        poly = clipPolygon(poly, pl);
      }
      for (let i = 1; i + 1 < poly.length / 3; i++) {
        out.push(poly[0], poly[1], poly[2],
          poly[i * 3], poly[i * 3 + 1], poly[i * 3 + 2],
          poly[i * 3 + 3], poly[i * 3 + 4], poly[i * 3 + 5]);
      }
    };
    const { elementIds, matrices } = model.boxes;
    for (let b = 0; b < elementIds.length; b++) {
      const eid = elementIds[b];
      if (!crosses(model, eid, plane)) continue;
      if (isVisible && !isVisible(eid)) continue;
      pts.length = 0;
      boxCrossings(matrices, b, plane, pts);
      emit();
    }
    for (const mm of model.meshes) {
      if (!crosses(model, mm.elementId, plane)) continue;
      if (isVisible && !isVisible(mm.elementId)) continue;
      pts.length = 0;
      meshCrossings(mm.verts, mm.index, plane, pts);
      emit();
    }
  }
  return out;
}

export type Scored = { index: number; score: number };

export function cosineTopK(
  query: ArrayLike<number>,
  matrix: ArrayLike<number>,
  dim: number,
  k: number,
): Scored[] {
  if (dim <= 0 || query.length < dim) return [];
  const count = Math.floor(matrix.length / dim);
  const scores: Scored[] = [];
  for (let i = 0; i < count; i += 1) {
    let dot = 0;
    const offset = i * dim;
    for (let d = 0; d < dim; d += 1) {
      dot += (query[d] ?? 0) * (matrix[offset + d] ?? 0);
    }
    scores.push({ index: i, score: dot });
  }
  scores.sort((a, b) => b.score - a.score);
  return scores.slice(0, k);
}

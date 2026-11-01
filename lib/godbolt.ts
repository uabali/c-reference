export function godboltUrl(
  code: string,
  compiler = "cclang1810",
  options = "-std=c23 -Wall -Wextra",
) {
  const state = {
    sessions: [
      {
        id: 1,
        language: "c",
        source: code,
        compilers: [{ id: compiler, libs: [], options }],
      },
    ],
  };
  const bytes = new TextEncoder().encode(JSON.stringify(state));
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  const b64 = btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/, "");
  return `https://godbolt.org/clientstate/${b64}`;
}

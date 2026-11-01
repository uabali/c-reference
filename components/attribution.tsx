export function Attribution({ source, title }: { source: string; title: string }) {
  return (
    <aside className="attribution">
      <p>
        Adapted from <a href={source}>{title}</a> on the{" "}
        <a href="https://en.cppreference.com/w/c">cppreference.com C reference</a>,
        licensed <a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0</a>.
        Offline text: PeterFeicht/cppreference-doc html-book v20250209, retrieved 2025-02-09.
        Sections labeled “Added on c.umutabali.com” are original commentary under the same license.
      </p>
    </aside>
  );
}

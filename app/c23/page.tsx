import Link from "next/link";
import { getC23Tables, referenceHref } from "@/lib/content";

export const metadata = { title: "C23 beside older C" };

export default function C23Page() {
  const table = getC23Tables();
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">C23 beside older C</h1>
      <p className="mt-2 max-w-3xl text-muted">{table.intro}</p>
      <div className="mt-6 overflow-x-auto rounded-2xl border border-line">
        <table className="min-w-full border-collapse text-sm">
          <thead className="bg-chip text-left">
            <tr>
              <th className="p-3">Feature</th>
              <th className="p-3">Older C</th>
              <th className="p-3">C23</th>
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row) => (
              <tr key={row.feature} className="border-t border-line align-top">
                <td className="p-3 font-semibold">
                  {row.page ? <Link className="text-accent" href={referenceHref(row.page)}>{row.feature}</Link> : row.feature}
                </td>
                <td className="p-3">{row.older}</td>
                <td className="p-3">{row.c23}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ul className="mt-4 max-w-3xl list-disc space-y-1 pl-5 text-sm text-muted">
        {table.notes.map((note) => <li key={note}>{note}</li>)}
      </ul>
    </main>
  );
}

#!/usr/bin/env python3
"""Write curated JSON consumed by the site. Does not touch converted MDX."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curated_part1 import CLANG, ENRICHMENT, ex
from curated_part2 import ENRICHMENT_2
from curated_part3 import ENRICHMENT_3


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    catalog = json.loads((repo / "content" / "catalog.json").read_text(encoding="utf-8"))
    titles = {page["slug"]: page["title"] for page in catalog["pages"]}
    rows = ENRICHMENT + ENRICHMENT_2 + ENRICHMENT_3
    missing = [row["slug"] for row in rows if row["slug"] not in titles]
    if missing:
        raise SystemExit(f"unknown slugs: {missing}")
    out = repo / "content" / "curated"
    out.mkdir(parents=True, exist_ok=True)
    (out / "enrichment.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    def step(slug: str, blurb: str) -> dict:
        if slug not in titles:
            raise SystemExit(f"path slug missing: {slug}")
        return {"slug": slug, "title": titles[slug], "blurb": blurb}

    paths = [
        {
            "slug": "memory",
            "title": "Pointers through dynamic memory",
            "minutes": 45,
            "summary": "The path most C programmers actually need: addresses, arrays, strings, the heap, structs, and calling a function by pointer.",
            "steps": [
                step("c/language/pointer", "An address you can store and follow. Initialize it, and know who owns the object."),
                step("c/language/array", "Contiguous objects. In a function parameter the array is already a pointer."),
                step("c/language/string_literal", "A static array with a hidden zero. Copy it before you edit it."),
                step("c/string/byte", "strlen, strcmp, and memcpy assume you know where the buffer ends."),
                step("c/memory/malloc", "Allocated storage outlives the function and starts uninitialized."),
                step("c/language/struct", "A layout of fields, with padding you do not get to interpret."),
                step("c/algorithm/qsort", "A function pointer is how the library calls back into your comparator."),
            ],
        },
        {
            "slug": "control",
            "title": "Control flow without surprises",
            "minutes": 25,
            "summary": "Branches, loops, and the places C lets execution jump farther than the next line.",
            "steps": [
                step("c/language/if", "A scalar compared with zero. Brace both sides."),
                step("c/language/for", "An index lives in the loop. Unsigned countdown is a trap."),
                step("c/language/switch", "Cases fall through until you stop them."),
                step("c/language/scope", "A name's visibility is not the same as its lifetime."),
                step("c/program/setjmp", "A non-local jump. Prefer it rarely, and mark the locals volatile."),
            ],
        },
        {
            "slug": "types",
            "title": "Types, qualifiers, and names",
            "minutes": 35,
            "summary": "What the bytes mean, what const actually promises, and how to name a function pointer.",
            "steps": [
                step("c/language/arithmetic_types", "Widths are minimums unless you ask stdint.h or _BitInt."),
                step("c/language/const", "A contract on one view of an object, not a lock."),
                step("c/language/volatile", "Every access is observable. It is not a lock either."),
                step("c/language/restrict", "A promise of no aliasing, which the compiler believes."),
                step("c/language/typedef", "An alias, not a new type. Watch what const does to a hidden pointer."),
                step("c/language/enum", "Names for integers. C23 can fix the width."),
                step("c/language/union", "One active member, ideally with a tag beside it."),
            ],
        },
        {
            "slug": "c23",
            "title": "What C23 changed in daily code",
            "minutes": 40,
            "summary": "The features worth using as soon as the compiler on the project actually has them.",
            "steps": [
                step("c/language/nullptr", "A null pointer that is not the integer zero."),
                step("c/language/attributes", "[[nodiscard]], [[fallthrough]], and the rest of the standard attributes."),
                step("c/language/attributes/nodiscard", "Make a dropped error code a warning."),
                step("c/language/constexpr", "A typed constant the compiler must fold."),
                step("c/language/typeof", "Name the type of an expression inside a macro."),
                step("c/language/arithmetic_types", "_BitInt(N) for a width the typedefs do not offer."),
                step("c/preprocessor/embed", "Include a file's bytes without a generated source file."),
                step("c/numeric/ckd_add", "Ask whether an addition fits, instead of hoping."),
            ],
        },
        {
            "slug": "text-io",
            "title": "Text and files",
            "minutes": 30,
            "summary": "From a literal, through formatting, to a stream you actually close.",
            "steps": [
                step("c/language/string_literal", "Where the characters come from."),
                step("c/string/byte/strlen", "A count of bytes before the zero, not a capacity."),
                step("c/string/byte/strcpy", "A copy that trusts the destination."),
                step("c/io/fprintf", "A format string that must match the arguments."),
                step("c/io/fopen", "A FILE you check, and a close you do not skip."),
                step("c/error/errno", "Read it only after a call has already failed."),
            ],
        },
    ]
    (out / "paths.json").write_text(json.dumps(paths, indent=2) + "\n", encoding="utf-8")

    edges = []

    def edge(source: str, target: str, kind: str) -> None:
        edges.append({"source": source, "target": target, "kind": kind})

    prereq = [
        ("c/language/pointer", "c/language/array"),
        ("c/language/array", "c/language/string_literal"),
        ("c/language/string_literal", "c/string/byte"),
        ("c/string/byte", "c/string/byte/strlen"),
        ("c/string/byte/strlen", "c/string/byte/strcpy"),
        ("c/string/byte/strlen", "c/string/byte/strcmp"),
        ("c/language/pointer", "c/memory/malloc"),
        ("c/memory/malloc", "c/memory/free"),
        ("c/memory/malloc", "c/memory/realloc"),
        ("c/language/pointer", "c/language/struct"),
        ("c/language/struct", "c/language/union"),
        ("c/language/pointer", "c/algorithm/qsort"),
        ("c/language/if", "c/language/for"),
        ("c/language/for", "c/language/switch"),
        ("c/language/switch", "c/program/setjmp"),
        ("c/language/arithmetic_types", "c/language/const"),
        ("c/language/const", "c/language/volatile"),
        ("c/language/volatile", "c/language/restrict"),
        ("c/language/typedef", "c/language/enum"),
        ("c/language/enum", "c/language/union"),
        ("c/types/NULL", "c/language/nullptr"),
        ("c/language/nullptr", "c/language/attributes"),
        ("c/language/attributes", "c/language/attributes/nodiscard"),
        ("c/language/attributes", "c/language/constexpr"),
        ("c/language/constexpr", "c/language/typeof"),
        ("c/language/typeof", "c/language/arithmetic_types"),
        ("c/preprocessor", "c/preprocessor/embed"),
        ("c/language/operator_arithmetic", "c/numeric/ckd_add"),
        ("c/language/string_literal", "c/io/fprintf"),
        ("c/io/fprintf", "c/io/fopen"),
        ("c/io/fopen", "c/error/errno"),
        ("c/language/struct", "c/language/alignof"),
        ("c/language/storage_duration", "c/memory/malloc"),
        ("c/language/scope", "c/language/storage_duration"),
        ("c/language/function_declaration", "c/language/function_definition"),
        ("c/language/function_definition", "c/algorithm/qsort"),
    ]
    for source, target in prereq:
        edge(source, target, "prerequisite")
    uses = [
        ("c/memory/free", "c/memory/malloc"),
        ("c/memory/realloc", "c/memory/malloc"),
        ("c/string/byte/strcpy", "c/string/byte/strlen"),
        ("c/io/fprintf", "c/language/string_literal"),
        ("c/algorithm/qsort", "c/language/pointer"),
        ("c/numeric/ckd_add", "c/language/operator_arithmetic"),
        ("c/language/alignof", "c/language/struct"),
        ("c/thread/thrd_create", "c/language/storage_duration"),
        ("c/language/atomic", "c/thread/thrd_create"),
        ("c/preprocessor/embed", "c/preprocessor"),
    ]
    for source, target in uses:
        edge(source, target, "uses")
    for item in edges:
        if item["source"] not in titles or item["target"] not in titles:
            raise SystemExit(f"bad edge {item}")
    (out / "edges.json").write_text(json.dumps(edges, indent=2) + "\n", encoding="utf-8")

    cards = [
        {
            "slug": "pointer",
            "title": "A pointer is an address",
            "minutes": 5,
            "difficulty": "Beginner",
            "page": "c/language/pointer",
            "lead": "The value of a pointer is where an object lives, or nullptr if it lives nowhere.",
            "points": [
                "Follow it with *p. Take an address with &object.",
                "p + 1 steps by one object, not one byte.",
                "The pointer does not own the object unless you decide it does.",
            ],
        },
        {
            "slug": "array-decay",
            "title": "Arrays decay",
            "minutes": 5,
            "difficulty": "Beginner",
            "page": "c/language/array",
            "lead": "In most expressions an array becomes a pointer to its first element. The length does not go with it.",
            "points": [
                "void f(int a[10]) is void f(int *a).",
                "sizeof keeps the length only while the name still denotes the array.",
                "Pass the count as a separate argument.",
            ],
        },
        {
            "slug": "string",
            "title": "A string is a zero",
            "minutes": 5,
            "difficulty": "Beginner",
            "page": "c/language/string_literal",
            "lead": "C text is an array of char whose last used element is zero. The library stops there.",
            "points": [
                "strlen does not count the zero. sizeof of a literal does.",
                "A literal is not writable.",
                "strncpy does not promise a terminator.",
            ],
        },
        {
            "slug": "malloc",
            "title": "malloc and free are a pair",
            "minutes": 5,
            "difficulty": "Beginner",
            "page": "c/memory/malloc",
            "lead": "The heap object lives until free, including after the function that allocated it returns.",
            "points": [
                "Check the pointer. Null means failure.",
                "The bytes are uninitialized.",
                "free(nullptr) is safe. free twice is not.",
            ],
        },
        {
            "slug": "struct-pad",
            "title": "Structs have holes",
            "minutes": 5,
            "difficulty": "Intermediate",
            "page": "c/language/struct",
            "lead": "The compiler inserts padding so each field is aligned. sizeof can be larger than the sum of the fields.",
            "points": [
                "Do not memcmp two structs if padding might differ.",
                "Reorder fields to shrink the object.",
                "A file format should use explicit widths, not the compiler's layout.",
            ],
        },
        {
            "slug": "ub",
            "title": "Undefined means no promise",
            "minutes": 5,
            "difficulty": "Intermediate",
            "page": "c/language/behavior",
            "lead": "If the standard says undefined, the compiler may assume that path never happens.",
            "points": [
                "Signed overflow, dangling pointers, and data races are in this bucket.",
                "A check after the bad access does not help.",
                "Sanitizers catch a lot of it. They are not a proof.",
            ],
        },
        {
            "slug": "const-volatile",
            "title": "const and volatile are not locks",
            "minutes": 5,
            "difficulty": "Intermediate",
            "page": "c/language/const",
            "lead": "const is a compile-time view. volatile is 'do not delete this access'. Neither one synchronizes threads.",
            "points": [
                "const int * and int * const are different.",
                "volatile ++ is not atomic.",
                "Shared flags between threads want stdatomic.h.",
            ],
        },
        {
            "slug": "nullptr-card",
            "title": "nullptr is not zero",
            "minutes": 5,
            "difficulty": "Beginner",
            "page": "c/language/nullptr",
            "lead": "C23 adds a null pointer constant with its own type, so it stops pretending to be an integer.",
            "points": [
                "It converts to any pointer type.",
                "It does not convert to an ordinary int.",
                "_Generic can tell it apart from 0.",
            ],
        },
        {
            "slug": "nodiscard-card",
            "title": "Do not drop the result",
            "minutes": 5,
            "difficulty": "Beginner",
            "page": "c/language/attributes/nodiscard",
            "lead": "[[nodiscard]] turns a discarded return value into a warning.",
            "points": [
                "Put it on error codes and on functions that allocate.",
                "(void)call() discards on purpose.",
                "The attribute belongs on the declaration the caller sees.",
            ],
        },
        {
            "slug": "checked-math",
            "title": "Ask if the add fits",
            "minutes": 5,
            "difficulty": "Intermediate",
            "page": "c/numeric/ckd_add",
            "lead": "ckd_add writes the wrapped result and returns true when the real result does not fit.",
            "points": [
                "A true return means do not use the value as a size.",
                "The type of the result pointer chooses the width.",
                "This header is C23.",
            ],
        },
        {
            "slug": "printf-card",
            "title": "The format string is code",
            "minutes": 5,
            "difficulty": "Beginner",
            "page": "c/io/fprintf",
            "lead": "printf trusts the format. A user-controlled format string is an attack, and a mismatched argument is undefined.",
            "points": [
                "Keep the format a literal.",
                "Use snprintf for a buffer, and read the returned length.",
                "%zu is size_t. %s of a null pointer is undefined.",
            ],
        },
        {
            "slug": "qsort-card",
            "title": "qsort calls you back",
            "minutes": 5,
            "difficulty": "Intermediate",
            "page": "c/algorithm/qsort",
            "lead": "The comparator is a function pointer. It must be a consistent order, and it must not overflow.",
            "points": [
                "Return (a > b) - (a < b), not a - b.",
                "Cast the const void * to the real element type.",
                "The sort is not required to be stable.",
            ],
        },
    ]
    (out / "cards.json").write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")

    mistakes = [
        {
            "title": "Returning the address of a local",
            "why": "The local dies when the function returns. The caller holds a pointer to storage that is gone.",
            "page": "c/language/storage_duration",
            "wrong": "int *bad(void) {\n    int n = 1;\n    return &n;\n}\n",
            "right": """
#include <stdlib.h>
int *good(void) {
    int *n = malloc(sizeof *n);
    if (n) *n = 1;
    return n;
}
int main(void) {
    int *p = good();
    if (!p || *p != 1) return 1;
    free(p);
    return 0;
}
""",
        },
        {
            "title": "sizeof on a decayed parameter",
            "why": "The parameter is a pointer. sizeof reports the pointer width, so a loop that trusts it walks the wrong number of bytes.",
            "page": "c/language/array",
            "wrong": "void fill(int a[8]) {\n    for (size_t i = 0; i < sizeof a / sizeof a[0]; i++) a[i] = 0;\n}\n",
            "right": """
#include <stdio.h>
void fill(size_t n, int *a) {
    for (size_t i = 0; i < n; i++) a[i] = 0;
}
int main(void) {
    int a[4] = {1, 2, 3, 4};
    fill(sizeof a / sizeof a[0], a);
    return a[3] == 0 ? 0 : 1;
}
""",
        },
        {
            "title": "strcpy into a short buffer",
            "why": "strcpy writes until the source zero, including that zero. A short destination overflows.",
            "page": "c/string/byte/strcpy",
            "wrong": "char buf[4];\nstrcpy(buf, \"hello\");\n",
            "right": """
#include <stdio.h>
int main(void) {
    char buf[4];
    int n = snprintf(buf, sizeof buf, "%s", "hello");
    return n == 5 && buf[0] == 'h' && buf[3] == '\\0' ? 0 : 1;
}
""",
        },
        {
            "title": "strcmp used as a boolean equality test",
            "why": "strcmp returns 0 when the strings match. A bare if (strcmp(a, b)) is true when they differ.",
            "page": "c/string/byte/strcmp",
            "wrong": "if (strcmp(name, \"ok\")) {\n    /* runs when they are NOT equal */\n}\n",
            "right": """
#include <stdio.h>
#include <string.h>
int main(void) {
    const char *name = "ok";
    if (strcmp(name, "ok") == 0) {
        puts("match");
        return 0;
    }
    return 1;
}
""",
        },
        {
            "title": "Overwriting the only realloc pointer",
            "why": "If realloc fails it returns null and leaves the old block allocated. Assigning through the same variable loses it.",
            "page": "c/memory/realloc",
            "wrong": "p = realloc(p, bigger);\nif (!p) {\n    /* the old block is leaked */\n}\n",
            "right": """
#include <stdlib.h>
#include <string.h>
int main(void) {
    char *p = malloc(4);
    if (!p) return 1;
    memcpy(p, "ab", 3);
    char *next = realloc(p, 8);
    if (!next) {
        free(p);
        return 1;
    }
    p = next;
    int ok = p[0] == 'a';
    free(p);
    return ok ? 0 : 1;
}
""",
        },
        {
            "title": "Signed overflow as a wrap",
            "why": "Signed overflow is undefined. The compiler may delete a check that would only be true if overflow had happened.",
            "page": "c/numeric/ckd_add",
            "wrong": "int saturating_add(int a, int b) {\n    int sum = a + b;\n    if (sum < a) return 2147483647;\n    return sum;\n}\n",
            "right": """
#include <stdckdint.h>
int saturating_add(int a, int b, int *out) {
    int sum = 0;
    if (ckd_add(&sum, a, b)) return -1;
    *out = sum;
    return 0;
}
int main(void) {
    int out = 0;
    return saturating_add(2, 3, &out) == 0 && out == 5 ? 0 : 1;
}
""",
        },
        {
            "title": "Reading errno after success",
            "why": "A successful library call is not required to clear errno. The value may belong to an earlier failure.",
            "page": "c/error/errno",
            "wrong": "FILE *fp = fopen(\"/\", \"r\");\n/* then, even if some later call succeeded */\nif (errno) perror(\"maybe unrelated\");\n",
            "right": """
#include <errno.h>
#include <stdio.h>
int main(void) {
    FILE *fp = fopen(\"/no/such/file-c-ref\", \"r\");
    if (!fp) {
        return errno != 0 ? 0 : 1;
    }
    fclose(fp);
    return 1;
}
""",
        },
        {
            "title": "A format string from the user",
            "why": "printf interprets % in the format. User text belongs in an argument, not in the format.",
            "page": "c/io/fprintf",
            "wrong": "void show(const char *user) {\n    printf(user);\n}\n",
            "right": """
#include <stdio.h>
void show(const char *user) {
    printf("%s\\n", user);
}
int main(void) {
    show("100% done");
    return 0;
}
""",
        },
        {
            "title": "qsort comparator that subtracts",
            "why": "INT_MAX - (-1) does not fit in int. The subtraction is signed overflow, which is undefined, and the sort becomes nonsense.",
            "page": "c/algorithm/qsort",
            "wrong": "int cmp(const void *x, const void *y) {\n    return *(const int *)x - *(const int *)y;\n}\n",
            "right": """
#include <stdlib.h>
int cmp(const void *x, const void *y) {
    int a = *(const int *)x;
    int b = *(const int *)y;
    return (a > b) - (a < b);
}
int main(void) {
    int a[] = {3, 1, 2};
    qsort(a, 3, sizeof *a, cmp);
    return a[0] == 1 && a[2] == 3 ? 0 : 1;
}
""",
        },
        {
            "title": "free, then touch",
            "why": "After free the pointer value is indeterminate. Comparing it or writing through it is undefined. Null your copy if you keep the variable.",
            "page": "c/memory/free",
            "wrong": "free(p);\nif (p) p->n = 0;\n",
            "right": """
#include <stdlib.h>
struct Node { int n; };
int main(void) {
    struct Node *p = malloc(sizeof *p);
    if (!p) return 1;
    p->n = 1;
    free(p);
    p = nullptr;
    free(p);
    return 0;
}
""",
        },
        {
            "title": "Missing void in an empty parameter list, the old way",
            "why": "Before C23, int f(); meant unspecified parameters. A call with the wrong arguments was not a constraint violation.",
            "page": "c/language/function_declaration",
            "wrong": "int f();\nint main(void) { return f(1, 2); }\n",
            "right": """
int f(void) { return 1; }
int main(void) { return f() == 1 ? 0 : 1; }
""",
        },
        {
            "title": "Unsigned loop that never ends",
            "why": "A size_t countdown of the form i >= 0 is always true, because an unsigned value cannot be negative.",
            "page": "c/language/for",
            "wrong": "for (size_t i = n; i >= 0; i--) {\n    use(i);\n}\n",
            "right": """
#include <stdio.h>
int main(void) {
    size_t n = 3;
    size_t sum = 0;
    for (size_t i = n; i-- > 0; ) sum += i;
    printf("%zu\\n", sum);
    return sum == 3 ? 0 : 1;
}
""",
        },
    ]
    (out / "mistakes.json").write_text(json.dumps(mistakes, indent=2) + "\n", encoding="utf-8")

    c23 = {
        "intro": "C23 is ISO/IEC 9899:2024. The rows below are the changes that show up in ordinary code. A feature being in the standard does not mean the compiler on a given machine has it: this site's examples were checked with Clang 18 (-std=c23) and GCC 13 (-std=c2x). Clang 18 here has nullptr, typeof, _BitInt, [[attributes]], stdckdint.h, and #elifdef. It does not have constexpr or #embed. GCC 13 has constexpr objects and not stdckdint.h or #embed.",
        "rows": [
            {"feature": "Null pointer", "older": "NULL, which may be 0 or (void *)0", "c23": "nullptr of type nullptr_t", "page": "c/language/nullptr"},
            {"feature": "Attributes", "older": "Vendor syntax such as __attribute__", "c23": "[[nodiscard]], [[maybe_unused]], [[deprecated]], [[fallthrough]], [[noreturn]]", "page": "c/language/attributes"},
            {"feature": "Checked calls", "older": "A comment that says check the return", "c23": "[[nodiscard]], optionally with a message", "page": "c/language/attributes/nodiscard"},
            {"feature": "Constants", "older": "Macros or enum", "c23": "constexpr objects, usable as array lengths", "page": "c/language/constexpr"},
            {"feature": "Type of an expression", "older": "GCC typeof as an extension", "c23": "typeof and typeof_unqual", "page": "c/language/typeof"},
            {"feature": "Exact integer width", "older": "stdint.h typedefs, when the platform has them", "c23": "_BitInt(N), no integer promotions", "page": "c/language/arithmetic_types"},
            {"feature": "Binary include", "older": "A generated .c array", "c23": "#embed", "page": "c/preprocessor/embed"},
            {"feature": "Overflow", "older": "Hand-written checks, easy to get wrong for signed types", "c23": "ckd_add, ckd_sub, ckd_mul in stdckdint.h", "page": "c/numeric/ckd_add"},
            {"feature": "Empty parameter list", "older": "int f(); meant unspecified arguments", "c23": "int f(); means int f(void);", "page": "c/language/function_declaration"},
            {"feature": "Zero a struct", "older": "= {0}", "c23": "= {} empty initializer", "page": "c/language/initialization"},
            {"feature": "bool", "older": "stdbool.h and the _Bool keyword", "c23": "bool, true, and false are keywords", "page": "c/language/arithmetic_types"},
            {"feature": "Alignment", "older": "_Alignas and _Alignof", "c23": "alignas and alignof", "page": "c/language/alignof"},
            {"feature": "Assertions", "older": "_Static_assert(expr, msg)", "c23": "static_assert, message optional", "page": "c/language/static_assert"},
            {"feature": "Duplicating a string", "older": "A POSIX strdup, not ISO", "c23": "strdup and strndup in string.h", "page": "c/string/byte"},
            {"feature": "Preprocessor", "older": "Nested #else / #ifdef", "c23": "#elifdef, #elifndef, #embed, __VA_OPT__", "page": "c/preprocessor"},
            {"feature": "auto", "older": "A storage-class leftover", "c23": "auto as type inference for an object with an initializer", "page": "c/language/declarations"},
        ],
        "notes": [
            "The comparison is about the language, not about one compiler's extensions. GCC accepted many of these as extensions before the standard did.",
            "constexpr functions and #embed are real C23, and they are the two items this project's compilers cannot check yet.",
            "Annex K bounds-checked functions (strcpy_s and the rest) remain optional. Do not treat them as the C23 story.",
        ],
    }
    (out / "c23.json").write_text(json.dumps(c23, indent=2) + "\n", encoding="utf-8")

    real = [
        {
            "slug": "arena",
            "title": "A bump allocator",
            "summary": "Parsers and compilers often allocate a pile of small objects that die together. An arena is a cursor into one buffer.",
            "compiler": "clang",
            "options": "-std=c23 -Wall -Wextra",
            "godboltCompiler": "cclang1810",
            "body": [
                "arena_alloc rounds the cursor up to the alignment, then hands back the next slice. Failure is a null pointer, the same contract as malloc, but free is 'throw the whole arena away'.",
                "This one uses a caller-provided buffer so the example has no hidden allocation. A production arena would grow with malloc.",
            ],
            "code": """
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef struct {
    unsigned char *base;
    size_t used;
    size_t cap;
} Arena;
void *arena_alloc(Arena *arena, size_t size, size_t align) {
    size_t pad = (align - (arena->used % align)) % align;
    if (size > arena->cap || pad > arena->cap - size || arena->used > arena->cap - size - pad) return nullptr;
    arena->used += pad;
    void *pointer = arena->base + arena->used;
    arena->used += size;
    return pointer;
}
int main(void) {
    unsigned char storage[64];
    Arena arena = { storage, 0, sizeof storage };
    int *number = arena_alloc(&arena, sizeof *number, alignof(int));
    char *text = arena_alloc(&arena, 4, 1);
    if (!number || !text) return 1;
    *number = 7;
    memcpy(text, "ok", 3);
    printf("%d %s\\n", *number, text);
    return *number == 7 && text[0] == 'o' ? 0 : 1;
}
""".strip() + "\n",
        },
        {
            "slug": "builder",
            "title": "A growing string",
            "summary": "Appending to a C string means owning the capacity, not calling strcat in a loop.",
            "compiler": "clang",
            "options": "-std=c23 -Wall -Wextra",
            "godboltCompiler": "cclang1810",
            "body": [
                "The buffer doubles when it is too small. realloc may move it, so the struct holds the only pointer.",
                "On failure the old contents stay valid, because the realloc result goes through a temporary.",
            ],
            "code": """
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { char *data; size_t len; size_t cap; } Buf;
int buf_append(Buf *buf, const char *text) {
    size_t extra = strlen(text);
    if (buf->len + extra + 1 < buf->len) return -1;
    if (buf->len + extra + 1 > buf->cap) {
        size_t cap = buf->cap ? buf->cap : 16;
        while (buf->len + extra + 1 > cap) {
            if (cap > (SIZE_MAX / 2)) return -1;
            cap *= 2;
        }
        char *next = realloc(buf->data, cap);
        if (!next) return -1;
        buf->data = next;
        buf->cap = cap;
    }
    memcpy(buf->data + buf->len, text, extra + 1);
    buf->len += extra;
    return 0;
}
int main(void) {
    Buf buf = {0};
    if (buf_append(&buf, "hello") || buf_append(&buf, " world")) return 1;
    printf("%s\\n", buf.data);
    int ok = strcmp(buf.data, "hello world") == 0;
    free(buf.data);
    return ok ? 0 : 1;
}
""".strip() + "\n",
        },
        {
            "slug": "callbacks",
            "title": "A table of commands",
            "summary": "A name and a function pointer is the smallest plugin table. qsort is the same idea with one slot.",
            "compiler": "clang",
            "options": "-std=c23 -Wall -Wextra",
            "godboltCompiler": "cclang1810",
            "body": [
                "The table is an array of structs. Lookup is a loop. The call is through the pointer, so adding a command does not add a branch at the call site.",
            ],
            "code": """
#include <stdio.h>
#include <string.h>
typedef int (*Command)(int);
int increment(int value) { return value + 1; }
int twice(int value) { return value * 2; }
int main(void) {
    struct { const char *name; Command fn; } table[] = {
        { "inc", increment },
        { "dbl", twice },
    };
    Command chosen = nullptr;
    for (size_t i = 0; i < sizeof table / sizeof table[0]; i++) {
        if (strcmp(table[i].name, "dbl") == 0) chosen = table[i].fn;
    }
    if (!chosen) return 1;
    printf("%d\\n", chosen(4));
    return chosen(4) == 8 ? 0 : 1;
}
""".strip() + "\n",
        },
        {
            "slug": "config",
            "title": "One line of configuration",
            "summary": "A lot of C tools start as a loop over key=value lines. The hazards are the missing equals sign and the buffer length.",
            "compiler": "clang",
            "options": "-std=c23 -Wall -Wextra",
            "godboltCompiler": "cclang1810",
            "body": [
                "parse refuses a missing separator and a key that does not fit. The value is copied with snprintf so it is terminated even when the source is longer than the destination.",
            ],
            "code": """
#include <stdio.h>
#include <string.h>
int parse_line(const char *line, char *key, size_t key_cap, char *value, size_t value_cap) {
    const char *eq = strchr(line, '=');
    if (!eq || eq == line || key_cap == 0 || value_cap == 0) return -1;
    size_t key_len = (size_t)(eq - line);
    if (key_len >= key_cap) return -1;
    memcpy(key, line, key_len);
    key[key_len] = '\\0';
    snprintf(value, value_cap, "%s", eq + 1);
    return 0;
}
int main(void) {
    char key[32], value[32];
    if (parse_line("port=8080", key, sizeof key, value, sizeof value)) return 1;
    if (parse_line("=nope", key, sizeof key, value, sizeof value) == 0) return 1;
    printf("%s %s\\n", key, value);
    return strcmp(key, "port") == 0 && strcmp(value, "8080") == 0 ? 0 : 1;
}
""".strip() + "\n",
        },
    ]
    (out / "real-world.json").write_text(json.dumps(real, indent=2) + "\n", encoding="utf-8")
    print(f"enrichment {len(rows)} paths {len(paths)} cards {len(cards)} mistakes {len(mistakes)} edges {len(edges)}")


if __name__ == "__main__":
    main()

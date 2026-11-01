"""Library and C23 notes."""

from curated_part1 import CLANG, CLANG_PTHREAD, ex

ENRICHMENT_3 = [
    {
        "slug": "c/language/generic",
        "difficulty": "Advanced",
        "why": "_Generic picks an expression based on the type of a controlling expression. It is C's type-generic macro tool, used by tgmath.h.",
        "when": "Use it when one macro must call a different function for float, double, and long double, or to reject a type. Do not use it as a poor substitute for a real function when one type is enough.",
        "pitfalls": [
            "The controlling expression is not evaluated, but its type is determined after the usual conversions of a value. A const int lvalue matches int, not const int, for the association.",
            "No implicit conversion is applied to find an association. int and long are different.",
        ],
        "practice": [
            "Always include a default association unless you want a constraint violation for unexpected types.",
            "Keep the macro a thin wrapper so the compiler still type-checks the chosen call.",
        ],
        "c23": "C23 lets you match nullptr_t, and the selection rules are tighter about qualified types. The feature itself arrived in C11.",
        "examples": [ex("Pick a function by type", """
#include <stdio.h>
int as_int(int x) { return x; }
int as_double(double x) { return (int)x; }
#define AS_INT(x) _Generic((x), int: as_int, double: as_double, default: as_int)(x)
int main(void) {
    printf("%d %d\\n", AS_INT(3), AS_INT(4.8));
    return AS_INT(3) == 3 && AS_INT(4.8) == 4 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/static_assert",
        "difficulty": "Intermediate",
        "why": "static_assert fails translation when a constant expression is false. It is how you pin a layout, a size, or an assumption before the program runs.",
        "when": "Assert sizes of file formats, the relationship between two constants, and that an enum value is what the protocol says.",
        "pitfalls": [
            "The expression must be an integer constant expression. A run-time value is a constraint violation, not a delayed check.",
            "A failing assert stops the build. Put the message where a reader can act on it.",
        ],
        "practice": [
            "Prefer static_assert over a run-time assert for facts that cannot change at run time.",
            "In C23 the message is optional. Keep a message when the failure would otherwise be a bare boolean.",
        ],
        "c23": "The keyword is static_assert, and the one-argument form static_assert(expr); is allowed. _Static_assert remains as the C11 spelling.",
        "examples": [ex("One-argument and two-argument forms", """
static_assert(sizeof(char) == 1);
static_assert(sizeof(int) >= 2, "int is unexpectedly narrow");
int main(void) { return 0; }
""")],
    },
    {
        "slug": "c/language/compound_literal",
        "difficulty": "Intermediate",
        "why": "A compound literal creates an unnamed object of a given type. It is how you pass a struct to a function without declaring a variable, and how you build a table in an expression.",
        "when": "Use one for a temporary struct argument or for a pointer to a short-lived aggregate. Do not use one when the object must outlive the block.",
        "pitfalls": [
            "At block scope the object has automatic storage. A pointer to it dangles after the block ends.",
            "At file scope it has static storage.",
        ],
        "practice": [
            "Combine it with designated initializers: (struct Point){ .x = 1, .y = 2 }.",
            "If a function stores the pointer, pass a real object with a lifetime you control.",
        ],
        "c23": "Compound literals can be constexpr, which gives them a permanent, constant identity. An ordinary block-scope literal is still automatic.",
        "examples": [ex("Pass a temporary struct", """
#include <stdio.h>
struct Point { int x, y; };
int sum(struct Point p) { return p.x + p.y; }
int main(void) {
    int n = sum((struct Point){ .x = 2, .y = 5 });
    printf("%d\\n", n);
    return n == 7 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/behavior",
        "difficulty": "Intermediate",
        "why": "The standard sorts behavior into defined, unspecified, implementation-defined, and undefined. Undefined behavior means the standard imposes no requirements, including on code that ran earlier in the same execution.",
        "when": "Read a library page's 'undefined' notes before wrapping the function. If your program depends on a particular compiler's reaction to UB, it is not a C program in the portable sense.",
        "pitfalls": [
            "A sanitizer clean run is not a proof. UB can be latent.",
            "Checking a pointer after you have already dereferenced it does not undo the violation.",
            "Signed overflow, out-of-bounds access, and use-after-free are the three that compilers exploit most aggressively.",
        ],
        "practice": [
            "Turn on -Wall -Wextra and the undefined-behavior sanitizer while developing.",
            "Write the precondition check before the operation, not after.",
        ],
        "examples": [ex("Check before dividing", """
#include <stdio.h>
int divide(int a, int b, int *out) {
    if (b == 0) return -1;
    *out = a / b;
    return 0;
}
int main(void) {
    int q = 0;
    int rc = divide(10, 2, &q);
    printf("%d %d\\n", rc, q);
    return rc == 0 && q == 5 && divide(1, 0, &q) == -1 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/scope",
        "difficulty": "Beginner",
        "why": "Scope is where a name is visible. It is not the same as storage duration. A static local has permanent storage and block scope.",
        "when": "Open a block to limit a name. Do not reuse a name from an outer scope unless shadowing is the point and the reader can see both.",
        "pitfalls": [
            "A declaration in a for loop's initializer is scoped to the loop.",
            "An identifier macro-expanded in a header can collide with a local name. That is why macros are spelled in capitals.",
        ],
        "practice": [
            "Declare a variable where you can initialize it, in the smallest block that needs it.",
            "File-scope names that are not part of the API should be static.",
        ],
        "examples": [ex("Inner name hides the outer one", """
#include <stdio.h>
int main(void) {
    int n = 1;
    {
        int n = 2;
        printf("%d\\n", n);
        if (n != 2) return 1;
    }
    return n == 1 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/preprocessor",
        "difficulty": "Beginner",
        "why": "The preprocessor rewrites tokens before the compiler parses them. It includes files, defines macros, and drops inactive branches.",
        "when": "Use it for include guards, for conditional compilation, and for macros that must be tokens. Prefer a constexpr, an inline function, or a typedef when those work.",
        "pitfalls": [
            "Macros do not respect scope or types, and they evaluate arguments every time they are spelled unless you capture them.",
            "A macro that looks like a function but uses its argument twice will double a side effect.",
        ],
        "practice": [
            "Parenthesize every macro parameter and the whole expression.",
            "Name macros in capitals so they look different from functions.",
        ],
        "c23": "#elifdef and #elifndef shorten nested feature tests. #embed pulls binary data in as integer tokens. __VA_OPT__ helps variadic macros.",
        "examples": [ex("#elifdef selects a branch", """
#include <stdio.h>
#define FEATURE 1
int main(void) {
    int mode = 0;
#if 0
    mode = 1;
#elifdef FEATURE
    mode = 2;
#else
    mode = 3;
#endif
    printf("%d\\n", mode);
    return mode == 2 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/preprocessor/embed",
        "difficulty": "Advanced",
        "why": "#embed is the C23 way to include a file's bytes as a comma-separated list of integer constants. It replaces the xxd-generated array that build scripts used to check in.",
        "when": "Use it for firmware blobs, certificates, and small assets that should live in the binary. Do not use it for files that change every run; those belong on disk.",
        "pitfalls": [
            "The resource is read during translation. A missing file is a build error, which is what you want, but it means the path must be stable.",
            "limit, prefix, suffix, and if_empty parameters change the token stream. A wrong prefix can break the surrounding syntax.",
        ],
        "practice": [
            "Give the array a const unsigned char type and an explicit length via sizeof.",
            "Keep the embedded file small enough that you are happy to recompile when it changes.",
        ],
        "c23": "#embed is C23. GCC 15 and recent Clang implement it. The compilers in this project's check (GCC 13, Clang 18) do not, so the runnable example is the array #embed would have produced.",
        "syntaxNote": {
            "title": "Syntax, not compiled here",
            "note": "This spelling needs a compiler with #embed, such as GCC 15. It is shown so the page is not missing the feature. The program under it is the equivalent that this project actually compiles.",
            "code": "const unsigned char blob[] = {\n#embed \"asset.bin\"\n};\n",
        },
        "examples": [ex("The array an embed would produce", """
#include <stdio.h>
const unsigned char blob[] = { 104, 105, 33 };
int main(void) {
    printf("%zu %c\\n", sizeof blob, blob[0]);
    return sizeof blob == 3 && blob[0] == 'h' ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/if",
        "difficulty": "Beginner",
        "why": "if selects a statement from a condition. The condition is compared with zero after the usual scalar conversions.",
        "when": "Use if for a branch. Use a switch when you are dispatching on several integer constants. Use a loop when the statement repeats.",
        "pitfalls": [
            "if (x = 1) assigns and is always true. The compiler warns; do not silence it blindly.",
            "A dangling else binds to the nearest if. Brace both branches.",
            "A pointer in a condition tests nullness. It does not test the pointee.",
        ],
        "practice": [
            "Always brace the body, even for one line.",
            "Compare explicitly when it reads better: if (p != nullptr).",
        ],
        "examples": [ex("Braced branches", """
#include <stdio.h>
const char *sign_of(int n) {
    if (n < 0) {
        return "neg";
    } else if (n > 0) {
        return "pos";
    } else {
        return "zero";
    }
}
int main(void) {
    printf("%s\\n", sign_of(-3));
    return sign_of(-3)[0] == 'n' ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/for",
        "difficulty": "Beginner",
        "why": "for packs initialization, a condition, and a step around a statement. It is the usual loop for an index.",
        "when": "Use for when the trip count is an index. Use while when the condition is an external event. Use do while when the body must run once.",
        "pitfalls": [
            "for (size_t i = n; i >= 0; i--) never ends if i is unsigned, because i >= 0 is always true.",
            "The comma operator in the step is easy to misread. Prefer a block if the step is complicated.",
        ],
        "practice": [
            "Declare the index in the for initializer so it does not leak.",
            "Walk arrays with an index or with a pointer plus an end pointer, and keep the end in view.",
        ],
        "c23": "You can declare a variable in the initializer, which C99 already allowed. C23 does not add a range-for.",
        "examples": [ex("Index stays in the loop", """
#include <stdio.h>
int main(void) {
    int sum = 0;
    for (int i = 1; i <= 4; i++) sum += i;
    printf("%d\\n", sum);
    return sum == 10 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/switch",
        "difficulty": "Intermediate",
        "why": "switch dispatches on an integer. Cases are labels, so execution falls through unless you break, return, or mark the fall-through.",
        "when": "Use switch for a closed set of integer codes. Use if for ranges and for non-integers.",
        "pitfalls": [
            "A missing break is usually a bug. C23's [[fallthrough]] makes the intentional ones visible.",
            "Case labels must be integer constant expressions, and they must be unique.",
            "Declarations inside a case need a brace if you want to initialize them, because of the jump.",
        ],
        "practice": [
            "End every case with break or [[fallthrough]].",
            "Keep a default that handles the unexpected value, even if it only returns an error.",
        ],
        "c23": "[[fallthrough]] is the portable annotation. A case can also use a constexpr name.",
        "examples": [ex("Intentional fall-through", """
#include <stdio.h>
int score(int kind) {
    int n = 0;
    switch (kind) {
    case 1:
        n += 10;
        [[fallthrough]];
    case 2:
        n += 1;
        break;
    default:
        n = -1;
        break;
    }
    return n;
}
int main(void) {
    printf("%d\\n", score(1));
    return score(1) == 11 && score(2) == 1 && score(9) == -1 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/string/byte/strlen",
        "difficulty": "Beginner",
        "why": "strlen counts bytes before the first zero. It does not know the size of the buffer, and it does not count the terminator.",
        "when": "Use it on a string you already trust. For a buffer that might not be terminated, scan with an explicit limit.",
        "pitfalls": [
            "strlen(NULL) is undefined.",
            "The result is size_t. Adding 1 for the terminator can wrap if the length is SIZE_MAX.",
        ],
        "practice": [
            "strnlen_s is the bounds-checked Annex K function. It is optional; do not assume it exists.",
            "If you have the capacity, stop at the capacity even when writing your own scan.",
        ],
        "examples": [ex("Length excludes the terminator", """
#include <stdio.h>
#include <string.h>
int main(void) {
    char buf[] = "abc";
    printf("%zu %zu\\n", strlen(buf), sizeof buf);
    return strlen(buf) == 3 && sizeof buf == 4 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/string/byte/strcpy",
        "difficulty": "Beginner",
        "why": "strcpy copies a C string, including the terminator. It has no size parameter, so the destination must already be large enough.",
        "when": "Use it only when the destination's capacity is known to be at least strlen(src) + 1. Otherwise copy with an explicit limit.",
        "pitfalls": [
            "The source and destination must not overlap. That is memmove's job, or a new buffer.",
            "strncpy is not the safe version. It can leave the destination unterminated, and it pads with zeros.",
        ],
        "practice": [
            "snprintf(dst, cap, \"%s\", src) terminates and reports how many characters it wanted to write.",
            "strdup (C23) is the allocating copy.",
        ],
        "examples": [ex("Copy into a buffer that fits", """
#include <stdio.h>
#include <string.h>
int main(void) {
    char dst[8];
    strcpy(dst, "cat");
    printf("%s\\n", dst);
    return strcmp(dst, "cat") == 0 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/string/byte/strcmp",
        "difficulty": "Beginner",
        "why": "strcmp compares two C strings lexicographically by unsigned char value. It returns zero when they are equal, not a boolean.",
        "when": "Use it for exact byte-string equality and ordering. Use strncmp when only a prefix should count. Locale-aware ordering is strcoll, which is slower and depends on setlocale.",
        "pitfalls": [
            "if (strcmp(a, b)) is true when they differ. Equality is strcmp(a, b) == 0.",
            "Both arguments must be terminated. A missing zero walks off the buffer.",
        ],
        "practice": [
            "Write the comparison with == 0 so the intent is obvious.",
            "For structs and binary blobs, use memcmp with an explicit length.",
        ],
        "examples": [ex("Equality is a zero result", """
#include <stdio.h>
#include <string.h>
int main(void) {
    int same = strcmp("abc", "abc") == 0;
    int less = strcmp("abc", "abd") < 0;
    printf("%d %d\\n", same, less);
    return same && less ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/string/byte/memcpy",
        "difficulty": "Intermediate",
        "why": "memcpy copies bytes. It does not stop at a zero, and it does not allow overlap. It is the fast path for objects and for non-overlapping buffers.",
        "when": "Use memcpy to copy a struct you are willing to copy as bytes, or a slice of an array. Use memmove if the ranges might overlap. Use strcpy only for C strings.",
        "pitfalls": [
            "Overlap is undefined for memcpy. memmove is the defined function.",
            "Copying a struct copies padding. That can leak stack bytes into a file or a hash.",
        ],
        "practice": [
            "Copy the size you mean: memcpy(dst, src, n * sizeof *dst) after checking the multiply.",
            "For a secret, memset_explicit (C23) is the wipe that compilers should not delete.",
        ],
        "examples": [ex("memmove overlaps, memcpy does not have to", """
#include <stdio.h>
#include <string.h>
int main(void) {
    char buf[8] = "abcdef";
    memmove(buf + 2, buf, 4);
    printf("%s\\n", buf);
    return memcmp(buf, "ababcd", 6) == 0 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/io/fprintf",
        "difficulty": "Beginner",
        "why": "printf and fprintf format values into text. The format string is a little language, and a mismatch with the arguments is undefined.",
        "when": "Use printf for diagnostics and text protocols you control. Use snprintf when the text must land in a buffer. Check the return value; it is the count written, or a negative error.",
        "pitfalls": [
            "A non-literal format string is a format-injection bug if it contains user text.",
            "%s with a null pointer is undefined. %zu is the specifier for size_t.",
            "sprintf has no size. It is the strcpy of formatting.",
        ],
        "practice": [
            "Keep the format a literal.",
            "snprintf(buf, sizeof buf, ...) and check that the returned length is non-negative and less than the size.",
        ],
        "c23": "There are new length modifiers for some bit-precise and decimal types, but the everyday specifiers are unchanged. The habit that matters is still snprintf.",
        "examples": [ex("snprintf reports truncation", """
#include <stdio.h>
int main(void) {
    char buf[4];
    int n = snprintf(buf, sizeof buf, "%s", "hello");
    printf("%d %s\\n", n, buf);
    return n == 5 && buf[3] == '\\0' ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/io/fopen",
        "difficulty": "Beginner",
        "why": "fopen connects a FILE to a path. The mode string selects read, write, append, and whether the file is text or binary.",
        "when": "Open a file when you need a stream. For a temporary file that should vanish, tmpfile is simpler and avoids a path.",
        "pitfalls": [
            "fopen returns null and sets errno. Ignoring the null crashes on the next call.",
            "On Windows, text mode translates newlines. Use \"rb\" and \"wb\" for bytes.",
            "A missing fclose leaks the descriptor. It also may drop a buffered write if you exit carelessly; fclose flushes.",
        ],
        "practice": [
            "Check the pointer, and check fclose if the write must hit disk.",
            "Prefer a bounded read (fread, fgets) over assuming the file fits.",
        ],
        "examples": [ex("tmpfile round trip", """
#include <stdio.h>
#include <string.h>
int main(void) {
    FILE *fp = tmpfile();
    if (!fp) return 1;
    if (fputs("hi\\n", fp) < 0) return 1;
    rewind(fp);
    char buf[8] = {0};
    if (!fgets(buf, sizeof buf, fp)) return 1;
    fclose(fp);
    printf("%s", buf);
    return strcmp(buf, "hi\\n") == 0 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/algorithm/qsort",
        "difficulty": "Intermediate",
        "diagram": "function-pointers",
        "why": "qsort sorts an array of objects of a size you specify, using a comparator you pass as a function pointer. It is the standard library's generic sort.",
        "when": "Use it for in-memory arrays of uniform objects. For a huge external sort or a stable sort, you need something else; qsort is not required to be stable.",
        "pitfalls": [
            "The comparator must impose a consistent order. Returning a - b for int can overflow.",
            "The pointer arguments are const void *. Cast them to the real type before reading.",
            "qsort on a null pointer with a positive count is undefined. A count of zero is fine.",
        ],
        "practice": [
            "Compare with < and > so the subtraction cannot overflow.",
            "Pass the element size with sizeof *a, not a magic number.",
        ],
        "examples": [ex("Sort three ints", """
#include <stdio.h>
#include <stdlib.h>
int cmp_int(const void *left, const void *right) {
    int a = *(const int *)left;
    int b = *(const int *)right;
    return (a > b) - (a < b);
}
int main(void) {
    int a[] = {3, 1, 2};
    qsort(a, 3, sizeof *a, cmp_int);
    printf("%d %d %d\\n", a[0], a[1], a[2]);
    return a[0] == 1 && a[1] == 2 && a[2] == 3 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/numeric/ckd_add",
        "difficulty": "Intermediate",
        "why": "ckd_add, ckd_sub, and ckd_mul perform integer arithmetic and tell you whether the mathematical result fits in the result type. The stored value is the wrapped low bits.",
        "when": "Use them for sizes, offsets, and any addition where overflow would be a security bug. They replace the hand-rolled checks that get the signed case wrong.",
        "pitfalls": [
            "A true return means overflow happened. The result is still written.",
            "The result pointer's type selects the width. Adding two ints into an int can overflow when adding them into a long long would not.",
        ],
        "practice": [
            "If the function returns true, do not use the result as a size.",
            "Include stdckdint.h. It is C23, so a C17 build will not have it.",
        ],
        "c23": "This header is new in C23. The example is checked with clang -std=c23, which provides stdckdint.h here. GCC 13 does not.",
        "examples": [ex("Detect an int overflow", """
#include <stdckdint.h>
#include <stdio.h>
int main(void) {
    int result = 0;
    bool overflow = ckd_add(&result, 2000000000, 2000000000);
    printf("%d\\n", overflow);
    return overflow ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/program/setjmp",
        "difficulty": "Advanced",
        "why": "setjmp and longjmp are a non-local goto. setjmp records the calling environment; longjmp restores it. They are how some C libraries implement error unwinding without a return code at every level.",
        "when": "Use them only for a well-defined failure path, usually inside one library. Prefer ordinary return codes for new code. Never use them as a general exception system across threads.",
        "pitfalls": [
            "After longjmp, non-volatile automatic objects that were modified after setjmp have indeterminate values.",
            "longjmp into a function that has already returned is undefined.",
            "Resources acquired between setjmp and longjmp are not released for you. Locks and FILE handles leak.",
        ],
        "practice": [
            "Mark locals that change between the two calls volatile.",
            "longjmp's second argument becomes the value setjmp returns. Use a non-zero value so it cannot be confused with the direct return.",
        ],
        "examples": [ex("Volatile step survives longjmp", """
#include <setjmp.h>
#include <stdio.h>
int main(void) {
    jmp_buf env;
    volatile int step = 0;
    if (setjmp(env) == 0) {
        step = 1;
        longjmp(env, 1);
    }
    printf("%d\\n", step);
    return step == 1 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/error/errno",
        "difficulty": "Beginner",
        "why": "errno is a thread-local integer that library functions set when they fail. It is not cleared on success, so you only read it after a function reports failure.",
        "when": "Read errno after fopen, strtol (when the return is the limit and you asked to detect range errors), and other functions whose specification says they set it.",
        "pitfalls": [
            "A successful call may leave errno unchanged. Checking it without a failure indication is a bug.",
            "errno is a macro. Taking its address is not portable in the way people expect; it may be a function call.",
        ],
        "practice": [
            "Set errno to 0 before a call only when the specification tells you to, as with strtol range detection.",
            "Use perror or strerror for a message, and remember strerror's static buffer is not a place to keep the string.",
        ],
        "examples": [ex("strtol reports a range error", """
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
int main(void) {
    errno = 0;
    char *end = 0;
    long value = strtol("999999999999999999999", &end, 10);
    printf("%ld %d\\n", value, errno);
    return errno == ERANGE ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/alignof",
        "difficulty": "Intermediate",
        "diagram": "padding",
        "why": "alignof yields the alignment requirement of a type. Allocators and packed formats need it so that a pointer is safe to dereference as that type.",
        "when": "Use it when you bump a cursor in an arena, or when you check that a buffer is aligned for an over-aligned type.",
        "pitfalls": [
            "A misaligned pointer cast to a stricter type is undefined on many architectures, not merely slow.",
            "alignof(char) is 1. alignof of a struct is the strictest member alignment.",
        ],
        "practice": [
            "Pair alignas on a declaration with alignof when you need a specific alignment.",
            "aligned_alloc requires the size to be a multiple of the alignment.",
        ],
        "c23": "The keyword is alignof. _Alignof is the older spelling and is obsolete. alignas likewise replaces _Alignas.",
        "examples": [ex("Over-aligned local", """
#include <stddef.h>
#include <stdio.h>
int main(void) {
    alignas(16) int slot = 1;
    printf("%zu %d\\n", alignof(int), slot);
    return ((unsigned long long)&slot % 16) == 0 && alignof(max_align_t) >= alignof(long) ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/thread/thrd_create",
        "difficulty": "Advanced",
        "why": "thrd_create starts a thread running a function of type int (*)(void *). It is the C11 standard thread, not POSIX pthread, though many libraries implement it on top of pthreads.",
        "when": "Use it when you want standard C threads and the platform provides them. Use pthreads or C11 threads consistently in one program; mixing locking rules is how deadlocks start.",
        "pitfalls": [
            "The thread function's argument must stay alive. A pointer to a loop variable is a race.",
            "A thread that is never joined and never detached leaks. Returning from main ends the process.",
            "This example links with -pthread.",
        ],
        "practice": [
            "Pass a pointer to a struct that the new thread owns, or that is immutable.",
            "Check the thrd_create result against thrd_success.",
        ],
        "c23": "C23 did not replace threads. It did make thread_local a keyword, which is how you give each thread its own object.",
        "examples": [ex("Join a worker", """
#include <stdio.h>
#include <threads.h>
int worker(void *arg) {
    int *slot = arg;
    *slot = 7;
    return 0;
}
int main(void) {
    int value = 0;
    thrd_t thread;
    if (thrd_create(&thread, worker, &value) != thrd_success) return 1;
    if (thrd_join(thread, 0) != thrd_success) return 1;
    printf("%d\\n", value);
    return value == 7 ? 0 : 1;
}
""", CLANG_PTHREAD, "Linked with -pthread.")],
    },
    {
        "slug": "c/language/atomic",
        "difficulty": "Advanced",
        "why": "An atomic object can be read and written from several threads without a data race. The memory order says how those accesses synchronize with other memory.",
        "when": "Use atomic_int for a counter or a published flag. Use a mutex when the invariant covers more than one word.",
        "pitfalls": [
            "A data race on a non-atomic object is undefined, not 'probably fine on x86'.",
            "memory_order_relaxed does not publish other writes. Release/acquire or a mutex does.",
            "Lock-free is not the same as wait-free, and atomic_is_lock_free can be false for a wide type.",
        ],
        "practice": [
            "Start with the sequential-consistency default. Drop to a weaker order only with a reason you can explain.",
            "Do not invent a lock out of volatile.",
        ],
        "c23": "The atomic library is C11. C23 clarifies some wording and adds more bit utilities elsewhere; the basic atomic_fetch_add pattern is unchanged.",
        "examples": [ex("A counter with the default order", """
#include <stdatomic.h>
#include <stdio.h>
int main(void) {
    atomic_int n = 0;
    atomic_fetch_add(&n, 1);
    int seen = atomic_load(&n);
    printf("%d\\n", seen);
    return seen == 1 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/memory/malloc",
        "difficulty": "Beginner",
        "diagram": "stack-heap",
        "why": "malloc allocates storage with allocated duration. The bytes are uninitialized. The pointer is the only way back to those bytes, and free is the only way to end their lifetime.",
        "when": "Use malloc when the size or the lifetime is not known at compile time. Use a local array when the size is small and bounded.",
        "pitfalls": [
            "A null return means failure. Using the pointer anyway is undefined.",
            "n * sizeof *p can overflow size_t before malloc sees it.",
            "The contents are indeterminate. Do not read them before a write.",
        ],
        "practice": [
            "Write T *p = malloc(n * sizeof *p); if (!p) handle it.",
            "calloc zeroes and checks the multiply. It is the right call when you need both.",
            "Every successful malloc has one free on every path, including errors.",
        ],
        "c23": "free_sized and free_aligned_sized are optional performance hints. They do not change the ownership rule. strdup is the allocating string copy.",
        "examples": [ex("Check the pointer, then free it", """
#include <stdio.h>
#include <stdlib.h>
int main(void) {
    size_t n = 4;
    int *p = malloc(n * sizeof *p);
    if (!p) return 1;
    for (size_t i = 0; i < n; i++) p[i] = (int)i;
    int ok = p[3] == 3;
    free(p);
    printf("%d\\n", ok);
    return ok ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/memory/free",
        "difficulty": "Beginner",
        "diagram": "stack-heap",
        "why": "free ends the lifetime of an object allocated by malloc, calloc, realloc, or aligned_alloc. After free, that pointer value is indeterminate.",
        "when": "Call free when the owner is done. Call it on every exit path. free(nullptr) is defined and does nothing, which makes cleanup code simpler.",
        "pitfalls": [
            "free of a pointer that was not returned by the allocator, or free twice, is undefined.",
            "Using the pointer after free is undefined, even to compare it. Set your copy to nullptr after free if you keep the variable.",
            "free of a stack address is undefined. So is free of the middle of an allocation.",
        ],
        "practice": [
            "Null the owner's pointer after free if anything else might look at it.",
            "Do not write a free wrapper that hides a null check; the library already does that.",
        ],
        "examples": [ex("free(nullptr) is safe", """
#include <stdlib.h>
int main(void) {
    int *p = 0;
    free(p);
    p = malloc(sizeof *p);
    if (!p) return 1;
    *p = 1;
    free(p);
    p = nullptr;
    free(p);
    return 0;
}
""")],
    },
    {
        "slug": "c/memory/realloc",
        "difficulty": "Intermediate",
        "diagram": "stack-heap",
        "why": "realloc grows or shrinks an allocation. It may move the block. On success the old pointer is no longer yours. On failure the old block is unchanged and the function returns null.",
        "when": "Use it to grow a buffer geometrically. Do not use it to 'free' by passing a size of zero if you care about portability; free is the clear call.",
        "pitfalls": [
            "p = realloc(p, n) leaks the old block when realloc fails and returns null, because you overwrote the only copy of the pointer.",
            "Pointers into the old block are invalid if realloc moved it.",
        ],
        "practice": [
            "Assign through a temporary: void *next = realloc(p, n); if (!next) { keep p; } else p = next;",
            "Grow by doubling so append is amortized constant time, and check the size for overflow.",
        ],
        "examples": [ex("Keep the old pointer if realloc fails", """
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(void) {
    char *p = malloc(4);
    if (!p) return 1;
    memcpy(p, "hi", 3);
    char *next = realloc(p, 8);
    if (!next) {
        free(p);
        return 1;
    }
    p = next;
    printf("%s\\n", p);
    int ok = p[0] == 'h';
    free(p);
    return ok ? 0 : 1;
}
""")],
    },
]

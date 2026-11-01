"""More original notes. Concatenated by tools/write_curated.py."""

from curated_part1 import CLANG, CLANG_PTHREAD, GCC, ex

ENRICHMENT_2 = [
    {
        "slug": "c/language/const",
        "difficulty": "Beginner",
        "why": "const documents that this view of an object is not used for writing. It is a compile-time contract on that expression, not a lock on the bytes.",
        "when": "Put const on pointer parameters that only read. Put it on tables that should live in read-only storage.",
        "pitfalls": [
            "const int * can still point at a non-const object. Another pointer may write it.",
            "Casting away const and writing an object that was defined const is undefined.",
            "const on a parameter passed by value only stops the function from reassigning its local copy.",
        ],
        "practice": [
            "Read the declaration from the identifier outward: const char * const p is a const pointer to const char.",
            "String literals should be seen through const char *.",
        ],
        "c23": "constexpr is a stronger promise than const: the object is a constant expression, not merely read-only.",
        "examples": [ex("Two different consts", """
#include <stdio.h>
int main(void) {
    int n = 1;
    const int *to_const = &n;
    int * const const_ptr = &n;
    n = 2;
    (void)to_const;
    printf("%d\\n", *const_ptr);
    return *const_ptr == 2 && *to_const == 2 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/volatile",
        "difficulty": "Intermediate",
        "why": "volatile tells the compiler that every access of this object is observable. Loads and stores may not be deleted or merged. That is what memory-mapped registers and signal handlers need.",
        "when": "Use volatile for a device register, or for a sig_atomic_t flag set from a signal handler. Do not use it as a mutex, a publish mechanism, or a substitute for atomic.",
        "pitfalls": [
            "volatile does not make a read-modify-write atomic. i++ on a volatile int can still tear.",
            "volatile does not order other memory. It is not a memory barrier.",
            "A pointer to volatile and a pointer to non-volatile are different types.",
        ],
        "practice": [
            "For shared flags between threads, use atomic_int from stdatomic.h.",
            "Access device registers through a volatile-qualified pointer whose address is fixed by the hardware, not by a guess.",
        ],
        "examples": [ex("A flag the compiler must reload", """
#include <stdio.h>
#include <signal.h>
static volatile sig_atomic_t stop = 0;
int main(void) {
    stop = 1;
    sig_atomic_t seen = stop;
    printf("%d\\n", (int)seen);
    return seen == 1 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/restrict",
        "difficulty": "Advanced",
        "why": "restrict is a promise that, for the lifetime of this pointer, the object it points at is not accessed through another pointer. The compiler can then keep values in registers and vectorize.",
        "when": "Use it on function parameters that are known not to alias, the way memcpy does and memmove deliberately does not. Do not sprinkle it on to silence a hunch.",
        "pitfalls": [
            "If the promise is false, the program is undefined. The bug looks like a miscompile.",
            "restrict on a local pointer does not change the caller's obligations by itself; the promise is about accesses based on that pointer.",
        ],
        "practice": [
            "memcpy is restrict. memmove is the function you call when the ranges might overlap.",
            "If you are not sure, leave restrict off. Correctness first.",
        ],
        "c23": "restrict itself is C99. C23 did not soften the aliasing rule.",
        "examples": [ex("Non-aliasing inputs", """
#include <stdio.h>
int add(int n, const int * restrict a, const int * restrict b) {
    int sum = 0;
    for (int i = 0; i < n; i++) sum += a[i] + b[i];
    return sum;
}
int main(void) {
    int a[2] = {1, 2};
    int b[2] = {3, 4};
    printf("%d\\n", add(2, a, b));
    return add(2, a, b) == 10 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/initialization",
        "difficulty": "Beginner",
        "why": "An uninitialized automatic object has an indeterminate value. Reading it is undefined. Initialization is how you avoid that, and how static-duration objects become zero before main.",
        "when": "Initialize at the declaration when you know the value. For a buffer you are about to fill completely, a later write is fine if every read happens after a write.",
        "pitfalls": [
            "int x; printf(\"%d\", x); is undefined, even if it prints 0 today.",
            "Partial initialization of a struct zeroes the rest. A partial array initializer zeroes the remaining elements too.",
            "Padding is not guaranteed to be zero just because you set the fields, unless the whole object was zeroed.",
        ],
        "practice": [
            "Zero a struct with = {0} or, in C23, = {}.",
            "Prefer designated initializers so a new field does not silently shift values.",
        ],
        "c23": "An empty initializer {} performs the same zero initialization as {0}, and it reads better for aggregates.",
        "examples": [ex("Empty initializer zeroes the rest", """
#include <stdio.h>
struct Pair { int a; int b; };
int main(void) {
    struct Pair p = { .a = 4 };
    int nums[4] = {};
    printf("%d %d\\n", p.b, nums[3]);
    return p.a == 4 && p.b == 0 && nums[3] == 0 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/typedef",
        "difficulty": "Beginner",
        "why": "typedef creates an alias for a type. It does not create a new type. The alias and the original are compatible.",
        "when": "Use it to name a complicated pointer, especially a function pointer, and to give a domain name to an integer (UserId) when a bare int would be vague.",
        "pitfalls": [
            "typedef hides a pointer sometimes (typedef char *String). That makes const String a const pointer, not a pointer to const.",
            "A typedef of an array decays the same way the array would.",
        ],
        "practice": [
            "Name function pointers: typedef int (*Cmp)(const void *, const void *);",
            "Do not typedef away a pointer unless the ownership story is part of the name.",
        ],
        "examples": [ex("A name for a function pointer", """
#include <stdio.h>
typedef int (*Binary)(int, int);
int add(int a, int b) { return a + b; }
int apply(Binary fn, int a, int b) { return fn(a, b); }
int main(void) {
    printf("%d\\n", apply(add, 20, 22));
    return apply(add, 20, 22) == 42 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/sizeof",
        "difficulty": "Beginner",
        "why": "sizeof yields the size in bytes of a type or of an expression. The expression is not evaluated, except for a variable-length array.",
        "when": "Use sizeof *p when allocating, so the type and the size cannot drift apart. Use sizeof buf for the capacity of a real array.",
        "pitfalls": [
            "sizeof on a pointer parameter is not the size of the array that decayed into it.",
            "sizeof(char) is 1 by definition. sizeof(int) is not required to be 4.",
            "The type of sizeof is size_t, which is unsigned. Mixing it with a negative int in a comparison is a classic bug.",
        ],
        "practice": [
            "Write malloc(n * sizeof *p) and check the multiplication for overflow before the call, or use calloc when zeroing is what you want.",
            "Parentheses are required for a type: sizeof(int). They are optional for an expression: sizeof x.",
        ],
        "c23": "sizeof remains unevaluated for ordinary expressions. _BitInt(N) has size large enough for N bits, rounded up to a byte, which you should measure with sizeof rather than guess.",
        "examples": [ex("Allocate with sizeof *p", """
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
        "slug": "c/language/operator_arithmetic",
        "difficulty": "Intermediate",
        "diagram": "pointers",
        "why": "Arithmetic operators are where C's integer and pointer rules show up. Integers promote, signed overflow is undefined, and pointer subtraction is only defined inside one array.",
        "when": "Use ordinary arithmetic for values. Use pointer arithmetic only to walk an array you already have the bounds for. Prefer an index if the bound check reads more clearly.",
        "pitfalls": [
            "Signed overflow is undefined. Unsigned overflow wraps.",
            "a / b truncates toward zero. a % b can be negative if a is negative.",
            "p + n is defined only when the result stays inside the same array or one past the end.",
        ],
        "practice": [
            "For a size calculation that might overflow, use the C23 checked arithmetic functions or check before multiplying.",
            "Subtract pointers only to get a ptrdiff_t distance within one array.",
        ],
        "c23": "stdckdint.h provides ckd_add, ckd_sub, and ckd_mul. They store the wrapped result and return true if the mathematical result does not fit.",
        "examples": [ex("Pointer stride is the element size", """
#include <stdio.h>
int main(void) {
    int a[4] = {10, 20, 30, 40};
    int *p = a;
    printf("%d\\n", *(p + 2));
    return (p + 2) - p == 2 && *(p + 2) == 30 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/cast",
        "difficulty": "Intermediate",
        "why": "A cast is an explicit conversion. C will also convert quietly in assignments and calls. The explicit form is how you say you meant the conversion, and how you convert a pointer.",
        "when": "Cast a void * back to the real pointer type after malloc or a generic API. Cast a numeric value when the conversion would otherwise surprise a reader. Do not cast to silence a warning you do not understand.",
        "pitfalls": [
            "Casting a pointer to an integer loses bits if the integer is too narrow. Use uintptr_t.",
            "A cast does not make an aliasing violation defined.",
            "(void)expr is the idiomatic way to discard a [[nodiscard]] result on purpose.",
        ],
        "practice": [
            "In C, malloc's void * converts to any object pointer without a cast. A cast is a C++ habit and can hide a missing declaration.",
            "Integer-to-pointer casts are implementation-defined and belong at the hardware boundary.",
        ],
        "examples": [ex("Round trip through void *", """
#include <stdio.h>
int main(void) {
    int n = 5;
    void *generic = &n;
    int *back = generic;
    printf("%d\\n", *back);
    return *back == 5 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/arithmetic_types",
        "difficulty": "Intermediate",
        "why": "The arithmetic types are the integers, the real floating types, and the complex types. Their widths are not fixed by the language except for the minimums in limits.h and the exact-width typedefs in stdint.h when the platform provides them.",
        "when": "Use int for ordinary counts that fit. Use size_t for object sizes. Use int32_t or uint64_t when the width is part of the contract. Use _BitInt(N) when you need a width the typedefs do not offer.",
        "pitfalls": [
            "char may be signed or unsigned. Do not assume either when the value may be above 127.",
            "Integer promotions lift small types to int before arithmetic. A uint16_t calculation can happen in signed int.",
            "long is 32 bits on Windows LLP64 and 64 bits on LP64 Unix. long long is at least 64 everywhere.",
        ],
        "practice": [
            "Include stdint.h and stddef.h for the names, not a home-grown header of guesses.",
            "Check conversions that might not fit. A cast is not a check.",
        ],
        "c23": "_BitInt(N) is an exact-width integer that does not undergo the integer promotions. unsigned _BitInt(N) wraps at N bits. Signed overflow is still undefined.",
        "examples": [ex("Wrapping 8-bit unsigned _BitInt", """
#include <stdio.h>
int main(void) {
    unsigned _BitInt(8) x = 255;
    x += 1;
    printf("%u\\n", (unsigned)x);
    return x == 0 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/nullptr",
        "difficulty": "Beginner",
        "why": "nullptr is a null pointer constant with its own type, nullptr_t. It converts to any pointer type and to bool, and it is not an integer 0.",
        "when": "Use nullptr for a new null pointer in C23 code. Keep NULL where you are matching an older codebase, but know that NULL may be defined as 0.",
        "pitfalls": [
            "nullptr does not convert to an ordinary integer type. If a macro is overloaded on int versus a pointer, nullptr selects the pointer side.",
            "Dereferencing nullptr is still undefined.",
        ],
        "practice": [
            "Prefer nullptr in new C23 code so _Generic can tell a null pointer from an integer zero.",
            "Check pointer returns before use. nullptr is a value, not a handler.",
        ],
        "c23": "This is a C23 feature. The type nullptr_t is declared in stddef.h.",
        "examples": [ex("nullptr is not an int", """
#include <stddef.h>
#include <stdio.h>
int main(void) {
    int kind = _Generic(nullptr, nullptr_t: 1, int: 2, default: 0);
    int *p = nullptr;
    printf("%d\\n", kind);
    return kind == 1 && p == nullptr ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/types/NULL",
        "difficulty": "Beginner",
        "why": "NULL is a macro for a null pointer constant. It has been the portable way to write a null pointer since C89, but the standard allows it to be defined as 0 or as (void *)0.",
        "when": "Use NULL in C89-through-C17 code and in APIs that already speak NULL. In new C23 code, nullptr is the sharper tool.",
        "pitfalls": [
            "If NULL is 0, _Generic(NULL, int: ..., void *: ...) can select the integer association.",
            "NULL is a pointer constant, not a null character. The terminator is '\\0', which is an int zero in a character context.",
        ],
        "practice": [
            "Do not redefine NULL.",
            "Include the header that documents the API (stddef.h, stdio.h, stdlib.h) rather than assuming a particular definition.",
        ],
        "c23": "nullptr does not replace NULL in old headers, but it removes the ambiguity for new code.",
        "examples": [ex("NULL compares equal to a null pointer", """
#include <stddef.h>
#include <stdio.h>
int main(void) {
    int *p = NULL;
    printf("%d\\n", p == NULL);
    return p == NULL ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/constexpr",
        "difficulty": "Intermediate",
        "why": "A constexpr object is a constant expression. You can use it for array lengths, case labels, and static initializers, and the compiler must be able to evaluate it during translation.",
        "when": "Use constexpr for named constants that used to be macros, when you want a type and a scope. A macro is still right for token pasting and for include guards.",
        "pitfalls": [
            "You cannot take a value that is only known at run time and mark it constexpr.",
            "C23 constexpr functions are more restricted than C++ constexpr functions, and GCC 13 accepts constexpr objects but not constexpr functions.",
        ],
        "practice": [
            "Prefer constexpr int N = 32; over #define N 32 for a typed constant.",
            "Keep macros for things the preprocessor must see, such as #if.",
        ],
        "c23": "constexpr on objects is the C23 replacement for many integer macros. The example below is checked with gcc -std=c2x because this environment's clang 18 does not implement constexpr yet.",
        "examples": [ex("Named constant used as an array length", """
#include <stdio.h>
int main(void) {
    constexpr int n = 6 * 7;
    int buf[n];
    buf[0] = 1;
    printf("%d\\n", n);
    return n == 42 && buf[0] == 1 ? 0 : 1;
}
""", GCC, "Compiled with gcc -std=c2x. GCC 13 implements constexpr objects, not constexpr functions.")],
    },
    {
        "slug": "c/language/attributes",
        "difficulty": "Intermediate",
        "why": "C23 standardizes attribute syntax, [[...]], for facts that are not part of the type system: nodiscard, maybe_unused, deprecated, fallthrough, noreturn, and the reproducibility attributes.",
        "when": "Use a standard attribute when you want a portable annotation. Use a vendor attribute (__attribute__, __declspec) only when the standard one does not exist.",
        "pitfalls": [
            "An unknown attribute is ignored, not rejected. A typo can vanish.",
            "[[fallthrough]] is a statement. It belongs where you intentionally drop into the next case, not as a decoration.",
        ],
        "practice": [
            "Mark functions whose return value must be checked with [[nodiscard]].",
            "Mark an intentional fall-through so -Wimplicit-fallthrough stays clean.",
        ],
        "c23": "The [[ ]] syntax and the standard attributes arrive with C23. Older code used compiler extensions that look similar but are not portable.",
        "examples": [ex("fallthrough and maybe_unused", """
#include <stdio.h>
int classify(int argc) {
    int n = 0;
    switch (argc) {
    case 1:
        n = 1;
        [[fallthrough]];
    default:
        n += 1;
        break;
    }
    return n;
}
int main(void) {
    [[maybe_unused]] int quiet = 0;
    printf("%d\\n", classify(1));
    return classify(1) == 2 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/attributes/nodiscard",
        "difficulty": "Beginner",
        "why": "[[nodiscard]] asks the compiler to warn when a caller ignores the return value. It is how you stop a checked error code from being thrown away.",
        "when": "Put it on functions that return an error code, an allocated pointer the caller must free, or any result that is the whole point of the call.",
        "pitfalls": [
            "The warning is not a hard error unless you build with -Werror.",
            "A cast to void is the way to discard the value on purpose. Do that only at the call site that means it.",
        ],
        "practice": [
            "You can attach a message: [[nodiscard(\"check the error\")]] int open_thing(void);",
            "Put the attribute on the declaration the caller sees, which usually means the header.",
        ],
        "c23": "[[nodiscard]] is standard in C23. Before that, compilers offered __attribute__((warn_unused_result)).",
        "examples": [ex("A result that is used", """
#include <stdio.h>
[[nodiscard]] int must_use(int x) { return x + 1; }
int main(void) {
    int y = must_use(3);
    printf("%d\\n", y);
    return y == 4 ? 0 : 1;
}
""")],
    },
    {
        "slug": "c/language/typeof",
        "difficulty": "Intermediate",
        "why": "typeof names the type of an expression. typeof_unqual names that type with the top-level qualifiers removed. They let a macro declare a temporary of the right type without the caller spelling it.",
        "when": "Use typeof in a macro that must work for several types, such as a swap or a max that should not evaluate an argument twice. Do not use it to hide a type that would be clearer written out.",
        "pitfalls": [
            "typeof keeps qualifiers. typeof of a const int is const int, which you cannot assign to. That is what typeof_unqual is for.",
            "The operand of typeof is not evaluated, but a variably modified type still needs its size expression to be valid.",
        ],
        "practice": [
            "In a macro, capture arguments in typeof_unqual temporaries so side effects run once.",
            "Prefer a plain declaration when the type is known.",
        ],
        "c23": "typeof and typeof_unqual are standardized in C23. GCC has had typeof as an extension for years; the unqual form is the new part.",
        "examples": [ex("Strip const with typeof_unqual", """
#include <stdio.h>
int main(void) {
    int n = 4;
    typeof(n) m = n * 2;
    const int c = 1;
    typeof_unqual(c) d = 2;
    d = 3;
    printf("%d %d\\n", m, d);
    return m == 8 && d == 3 ? 0 : 1;
}
""")],
    },
]

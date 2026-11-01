"""Original C reference notes. Imported by tools/write_curated.py."""

CLANG = {
    "compiler": "clang",
    "options": "-std=c23 -Wall -Wextra",
    "godboltCompiler": "cclang1810",
}
GCC = {
    "compiler": "gcc",
    "options": "-std=c2x -Wall -Wextra",
    "godboltCompiler": "cg133",
}
CLANG_PTHREAD = {**CLANG, "options": "-std=c23 -Wall -Wextra -pthread"}


def ex(title, code, base=CLANG, note=""):
    item = {**base, "title": title, "code": code.strip() + "\n"}
    if note:
        item["note"] = note
    return item


ENRICHMENT = [
    {
        "slug": "c/language/pointer",
        "difficulty": "Beginner",
        "diagram": "pointers",
        "why": "A pointer is an address you can store, copy, and follow. C uses that one mechanism for out-parameters, dynamic objects, optional values, and callbacks.",
        "when": "Use a pointer when a function must change a caller's object, when the object's lifetime is not the caller's frame, or when the callee should not know the concrete type (void *). Prefer a plain value or an index when the data already lives in an array you own.",
        "pitfalls": [
            "Dereferencing an uninitialized or null pointer is undefined behavior, not a reliable crash.",
            "A pointer to a local variable dies with that frame. Returning &local is a dangling pointer.",
            "Pointer arithmetic is only defined inside an array, or one past its end. You may not dereference one past the end.",
            "Casting a pointer to an unrelated object type and then reading it breaks strict aliasing, except for char * and similar special cases.",
        ],
        "practice": [
            "Initialize every pointer. C23's nullptr is a pointer constant and is clearer than 0.",
            "Decide who frees the object. One owner, documented at the function boundary.",
            "Write const on the pointee when the function only reads: const int *.",
            "int * const is a const pointer. const int * is a pointer to const. They are not the same.",
        ],
        "c23": "nullptr has type nullptr_t and converts to any pointer type. It does not convert to an ordinary integer the way a bare 0 does, which matters for _Generic and overloaded macros.",
        "examples": [
            ex("Swap through pointers", """
#include <stdio.h>
void swap(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}
int main(void) {
    int x = 1, y = 2;
    swap(&x, &y);
    printf("%d %d\\n", x, y);
    return x == 2 && y == 1 ? 0 : 1;
}
"""),
            ex("Call through a function pointer", """
#include <stdio.h>
int apply(int value, int (*fn)(int)) { return fn(value); }
int square(int value) { return value * value; }
int main(void) {
    int (*fp)(int) = square;
    printf("%d\\n", apply(5, fp));
    return fp(5) == 25 ? 0 : 1;
}
"""),
        ],
    },
    {
        "slug": "c/language/array",
        "difficulty": "Beginner",
        "diagram": "arrays",
        "why": "An array is a contiguous sequence of objects. In almost every expression it decays to a pointer to its first element, which is why function parameters written as int a[10] are actually int *.",
        "when": "Use an array when the count is known and the storage should live with the owner: a local buffer, a field in a struct, or a file-scope table. Use malloc when the count is only known at run time.",
        "pitfalls": [
            "sizeof on a decayed parameter is the size of a pointer, not the array.",
            "There is no bounds check. a[i] and *(a + i) are the same, including the lack of a check.",
            "A variable-length array is an automatic object. A huge VLA can blow the stack, and VLAs are optional in C11 and later.",
        ],
        "practice": [
            "Pass the length beside the pointer: void fill(size_t n, int *a).",
            "Prefer int a[static 1] in a prototype when a null pointer is not allowed (C99).",
            "For a compile-time count, sizeof a / sizeof a[0] works only while a is still an array.",
        ],
        "c23": "Empty initialization int a[4] = {}; zeroes the array. The old idiom was = {0}, which is still fine.",
        "examples": [
            ex("sizeof stays with the array", """
#include <stdio.h>
size_t words(const char *s) { return sizeof s; }
int main(void) {
    char buf[] = "Hi";
    printf("array %zu pointer-param %zu\\n", sizeof buf, words(buf));
    return sizeof buf == 3 ? 0 : 1;
}
"""),
        ],
    },
    {
        "slug": "c/language/string_literal",
        "difficulty": "Beginner",
        "diagram": "arrays",
        "why": "A string literal is a static array of char that already contains the terminating null. It is how most C text enters a program, and it is not a String object.",
        "when": "Use a literal for fixed messages and keys. Copy it into an array or into malloc storage when the program needs to edit the characters.",
        "pitfalls": [
            "Writing through a pointer to a literal is undefined. char *p = \"Hi\"; p[0] = 'h'; is not allowed.",
            "Adjacent literals concatenate in translation, which can hide a missing comma in an array initializer.",
            "The size of the literal includes the null. sizeof \"Hi\" is 3, while the text length is 2.",
        ],
        "practice": [
            "Point at a literal with const char * so the compiler rejects writes.",
            "char buf[] = \"Hi\"; makes a writable copy.",
            "UTF-8 literals (u8\"...\") are char8_t arrays in C23, not a different runtime string type.",
        ],
        "c23": "char8_t is a distinct type for UTF-8 text. u8 literals have type char8_t[N]. Mixing them with char * may need an explicit cast.",
        "examples": [
            ex("Copy a literal before editing", """
#include <stdio.h>
#include <string.h>
int main(void) {
    const char *literal = "Hi";
    char buf[] = "Hi";
    buf[0] = 'h';
    printf("%s %zu\\n", buf, sizeof literal);
    return buf[0] == 'h' && literal[2] == '\\0' ? 0 : 1;
}
"""),
        ],
    },
    {
        "slug": "c/string/byte",
        "difficulty": "Beginner",
        "diagram": "arrays",
        "why": "The byte-string functions in string.h are the standard library's text tools. They all assume a terminating zero unless the name says otherwise (strncmp, memcpy, memchr).",
        "when": "Use them for C strings you already own. For untrusted input with a known buffer size, prefer the bounded forms: snprintf, and memchr or an explicit length, not unbounded strcpy.",
        "pitfalls": [
            "strlen on a pointer that is not terminated reads off the end of the buffer.",
            "strncpy does not always write a terminator. It is a poor 'safe strcpy'.",
            "strcat and sprintf share the same overflow story as strcpy.",
        ],
        "practice": [
            "Keep the capacity next to the pointer and refuse to walk past it.",
            "strdup (C23) allocates a copy; you still have to free it.",
            "memcmp compares bytes. strcmp compares C strings and stops at the first zero.",
        ],
        "c23": "strdup and strndup are standard. memset_explicit is the function you want when a compiler might otherwise delete a wipe of a secret.",
        "examples": [
            ex("Bounded copy that always terminates", """
#include <stdio.h>
#include <string.h>
void copy_bounded(char *dst, size_t cap, const char *src) {
    if (cap == 0) return;
    size_t n = 0;
    while (n + 1 < cap && src[n] != '\\0') {
        dst[n] = src[n];
        n++;
    }
    dst[n] = '\\0';
}
int main(void) {
    char buf[4];
    copy_bounded(buf, sizeof buf, "hello");
    printf("%s\\n", buf);
    return strcmp(buf, "hel") == 0 ? 0 : 1;
}
"""),
        ],
    },
    {
        "slug": "c/language/struct",
        "difficulty": "Beginner",
        "diagram": "padding",
        "why": "A struct is a named layout of objects. It is the usual way to keep related data together and to pass that bundle by pointer.",
        "when": "Use a struct when several values form one object: a point, a buffer plus its length, a file header. Use separate variables only when they are not a unit.",
        "pitfalls": [
            "Padding bytes are not yours to interpret. Comparing structs with memcmp can fail because padding is unspecified.",
            "Field order changes sizeof. A char between two doubles is expensive.",
            "A flexible array member must be last, and the struct is allocated with room for the tail.",
        ],
        "practice": [
            "Pass structs larger than a couple of words by pointer. Pass small ones by value when you want a copy.",
            "Initialize with designated initializers: (struct Point){ .x = 1 }.",
            "If the layout is an external file format, use explicit widths and do not trust the compiler's padding.",
        ],
        "c23": "Designated initializers can be mixed more freely than in C99, and empty initialization zeroes the object. constexpr can name a compound literal that is a constant.",
        "examples": [
            ex("Designated initializer and sizeof", """
#include <stdio.h>
struct Sample {
    char tag;
    int count;
    char flag;
};
int main(void) {
    struct Sample s = { .count = 3, .tag = 'A' };
    printf("%zu %d\\n", sizeof s, s.count);
    return s.count == 3 && s.flag == 0 ? 0 : 1;
}
"""),
        ],
    },
    {
        "slug": "c/language/union",
        "difficulty": "Intermediate",
        "why": "A union stores one of several types in the same memory. It is the right tool for a tagged value, a register that has several views, or a careful type pun.",
        "when": "Use a union with a tag when a value is an int or a pointer or a double, not all at once. Do not use it as a shortcut to break aliasing unless the read is through the union that wrote the value, which C permits as type punning.",
        "pitfalls": [
            "Reading a member that is not the active one is not a general conversion. Float bits read as int are a pun, not a cast.",
            "The size is the largest member, plus padding for alignment.",
            "A union does not track which member is active. If you need that, store a tag beside it.",
        ],
        "practice": [
            "Put the union inside a struct with an enum tag.",
            "For numeric conversion, write a cast. For bit reinterpretation, a union or memcpy is the honest tool.",
        ],
        "c23": "Unions may be empty-initialized, which sets the first member to zero. That does not make the other members 'active' in a way you should rely on for trap representations.",
        "examples": [
            ex("Tagged union", """
#include <stdio.h>
enum Kind { KIND_INT, KIND_PTR };
struct Value {
    enum Kind kind;
    union {
        int number;
        int *pointer;
    } as;
};
int read_int(struct Value v) {
    return v.kind == KIND_INT ? v.as.number : -1;
}
int main(void) {
    struct Value v = { .kind = KIND_INT, .as.number = 9 };
    printf("%d\\n", read_int(v));
    return read_int(v) == 9 ? 0 : 1;
}
"""),
        ],
    },
    {
        "slug": "c/language/enum",
        "difficulty": "Beginner",
        "why": "An enumeration gives names to integer constants. It documents a closed set of choices better than a pile of macros.",
        "when": "Use an enum for states, tags, and options that are integers. Do not use it when the values must be a specific width on disk; an enum's underlying type was historically int.",
        "pitfalls": [
            "Enumerators are integer constants. Nothing stops you assigning an out-of-range int to an enum object.",
            "Two enumerations are not distinct types for the type checker the way they are in C++. A function taking one enum will accept another.",
        ],
        "practice": [
            "Give the enum a name and use it in function signatures so readers see the unit.",
            "If you need a specific representation, set the values explicitly and static_assert the ones that matter.",
        ],
        "c23": "C23 lets you specify the underlying type, for example enum Color : unsigned char { RED, GREEN }. That fixes the width.",
        "examples": [
            ex("Named states", """
#include <stdio.h>
enum State { STATE_IDLE, STATE_RUN, STATE_DONE };
const char *name(enum State state) {
    switch (state) {
    case STATE_IDLE: return "idle";
    case STATE_RUN: return "run";
    case STATE_DONE: return "done";
    }
    return "?";
}
int main(void) {
    printf("%s\\n", name(STATE_RUN));
    return STATE_DONE == 2 ? 0 : 1;
}
"""),
        ],
    },
    {
        "slug": "c/language/function_declaration",
        "difficulty": "Beginner",
        "why": "A declaration introduces a function's type without defining it. Headers are full of them so callers and the definition agree.",
        "when": "Put declarations in a header when more than one file calls the function. Keep a static function's declaration in the .c file, or just define it before use.",
        "pitfalls": [
            "An old-style declaration void f(); means 'unspecified arguments', not 'no arguments'. void f(void); means no arguments.",
            "A declaration and a definition with incompatible types is undefined, often only caught by the linker or not at all if they are in different translation units without a shared header.",
        ],
        "practice": [
            "Always write a prototype. Always write (void) for an empty parameter list.",
            "Include the header in the file that defines the function, so the compiler checks the definition against the declaration.",
        ],
        "c23": "A parameter list () is treated as (void). The old unspecified-argument meaning is gone. [[nodiscard]] can sit on the declaration.",
        "examples": [
            ex("Prototype checked against the call", """
#include <stdio.h>
int add(int a, int b);
int main(void) {
    printf("%d\\n", add(2, 3));
    return add(2, 3) == 5 ? 0 : 1;
}
int add(int a, int b) { return a + b; }
"""),
        ],
    },
    {
        "slug": "c/language/function_definition",
        "difficulty": "Beginner",
        "why": "A definition is the function body. It is also a declaration. One definition of an external function may exist in the whole program.",
        "when": "Define a function in a .c file. Mark it static if no other file should see it. That also allows the compiler to inline and drop it.",
        "pitfalls": [
            "Forgetting static on a helper can collide with the same name in another file at link time.",
            "A function that returns a pointer to its own local variable hands the caller a dead address.",
            "main should be int main(void) or int main(int argc, char **argv). Other signatures are not portable.",
        ],
        "practice": [
            "Keep functions short enough that the error paths are visible.",
            "Return an error code or write through an out-parameter. Do not hide failure.",
        ],
        "c23": "You can repeat the constexpr and attribute story on a definition. constexpr functions exist in C23 but need a newer compiler than the GCC 13 used to check the object form on this site.",
        "examples": [
            ex("static helper", """
#include <stdio.h>
static int twice(int n) { return n * 2; }
int main(void) {
    printf("%d\\n", twice(21));
    return twice(21) == 42 ? 0 : 1;
}
"""),
        ],
    },
    {
        "slug": "c/language/storage_duration",
        "difficulty": "Intermediate",
        "diagram": "stack-heap",
        "why": "Storage duration is when an object's memory exists. Automatic objects die with the block. Static objects live for the whole program. Allocated objects live until free.",
        "when": "Use automatic storage for ordinary locals. Use static for tables and for state that must outlive a call and is not shared across threads. Use malloc when the lifetime or size is dynamic.",
        "pitfalls": [
            "A static local is shared by every caller and is not reset between calls. It is also a race if two threads enter the function.",
            "Returning the address of an automatic object is the classic dangling pointer.",
            "thread_local is a fourth duration. A plain static is not per-thread.",
        ],
        "practice": [
            "Name the owner of allocated storage in the function comment.",
            "Do not use static locals as a hidden cache unless the data is immutable after init.",
        ],
        "c23": "thread_local is a real keyword, not only the _Thread_local macro. The durations themselves are unchanged.",
        "examples": [
            ex("Automatic versus static", """
#include <stdio.h>
int next_id(void) {
    static int id = 0;
    return ++id;
}
int main(void) {
    int local = 1;
    int a = next_id();
    int b = next_id();
    printf("%d %d %d\\n", local, a, b);
    return a == 1 && b == 2 ? 0 : 1;
}
"""),
        ],
    },
]

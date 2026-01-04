#ifndef STUDENT_DSA_SHARED_H
#define STUDENT_DSA_SHARED_H

#include <stddef.h>

#ifdef _WIN32
  #ifdef BUILDING_DLL
    #define DLLEXPORT __declspec(dllexport)
  #else
    #define DLLEXPORT __declspec(dllimport)
  #endif
#else
  #define DLLEXPORT __attribute__((visibility("default")))
#endif

typedef void* DSAHandle;

DLLEXPORT DSAHandle load_from_string(const char* data);
DLLEXPORT DSAHandle load_from_file(const char* path);
DLLEXPORT void free_handle(DSAHandle h);

DLLEXPORT int sort_by_roll(DSAHandle h);
DLLEXPORT int sort_by_name(DSAHandle h);

DLLEXPORT int search_roll(DSAHandle h, int key, char* outbuf, size_t bufsz);

DLLEXPORT int stats(DSAHandle h, int* count, double* avg, int* minv, int* maxv);

DLLEXPORT int export_to_string(DSAHandle h, char** outbuf, size_t* outlen);
DLLEXPORT void free_string(char* s);

DLLEXPORT int export_to_file(DSAHandle h, const char* path);

#endif

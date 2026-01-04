#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "student_dsa_shared.h"

#ifndef DLLEXPORT
  #define DLLEXPORT
#endif

#define MAX_NAME_LEN 256

typedef struct {
    int roll;
    char name[MAX_NAME_LEN];
    int marks;
} Student;

typedef struct {
    Student *arr;
    size_t n;
} Data;

static void trim_newline(char *s){
    size_t i = strlen(s);
    while(i>0 && (s[i-1]=='\n' || s[i-1]=='\r')) { s[i-1]=0; i--; }
}

static int parse_line_to_student(char *line, Student *out){
    trim_newline(line);
    if (line[0] == 0) return -1;
    char *p = line;
    char *tok;

    tok = strtok(p, ",");
    if (!tok) return -1;
    out->roll = atoi(tok);

    tok = strtok(NULL, ",");
    if (!tok) return -1;
    strncpy(out->name, tok, MAX_NAME_LEN-1);
    out->name[MAX_NAME_LEN-1] = '\0';

    tok = strtok(NULL, ",");
    if (!tok) return -1;
    out->marks = atoi(tok);

    return 0;
}

static Data* data_from_string(const char* data_str){
    if (!data_str) return NULL;
    char *copy = strdup(data_str);
    if (!copy) return NULL;
    size_t cap = 64;
    Student *arr = malloc(sizeof(Student) * cap);
    if (!arr){ free(copy); return NULL; }
    size_t n = 0;

    char *saveptr = NULL;
    char *line = strtok_r(copy, "\n", &saveptr);
    while (line){
        char *tmp = line;
        while (*tmp && isspace((unsigned char)*tmp)) tmp++;
        if (*tmp != '\0'){
            if (n + 1 > cap){
                cap *= 2;
                Student *tmpa = realloc(arr, cap * sizeof(Student));
                if (!tmpa){ free(arr); free(copy); return NULL; }
                arr = tmpa;
            }
            char *line_copy = strdup(line);
            if (!line_copy) { free(arr); free(copy); return NULL; }
            if (parse_line_to_student(line_copy, &arr[n]) == 0){
                n++;
            }
            free(line_copy);
        }
        line = strtok_r(NULL, "\n", &saveptr);
    }
    free(copy);
    Data *d = malloc(sizeof(Data));
    if (!d){ free(arr); return NULL; }
    d->arr = arr;
    d->n = n;
    return d;
}

static Data* data_from_file(const char* path){
    FILE *f = fopen(path, "r");
    if (!f) return NULL;
    size_t cap = 64;
    Student *arr = malloc(sizeof(Student) * cap);
    if (!arr){ fclose(f); return NULL; }
    size_t n = 0;
    char buf[512];
    while (fgets(buf, sizeof(buf), f)){
        char *p = buf;
        while (*p && isspace((unsigned char)*p)) p++;
        if (*p == 0) continue;
        if (n + 1 > cap){
            cap *= 2;
            Student *tmpa = realloc(arr, cap * sizeof(Student));
            if (!tmpa){ free(arr); fclose(f); return NULL; }
            arr = tmpa;
        }
        char *line_copy = strdup(buf);
        if (!line_copy){ free(arr); fclose(f); return NULL; }
        if (parse_line_to_student(line_copy, &arr[n]) == 0){
            n++;
        }
        free(line_copy);
    }
    fclose(f);
    Data *d = malloc(sizeof(Data));
    if (!d){ free(arr); return NULL; }
    d->arr = arr;
    d->n = n;
    return d;
}

/* Compare functions */
static int cmp_roll(const void *a, const void *b){
    const Student *pa = a, *pb = b;
    return (pa->roll - pb->roll);
}
static int cmp_name(const void *a, const void *b){
    const Student *pa = a, *pb = b;
    return strcasecmp(pa->name, pb->name);
}

/* API implementations */
DLLEXPORT DSAHandle load_from_string(const char* data){
    return (DSAHandle)data_from_string(data);
}

DLLEXPORT DSAHandle load_from_file(const char* path){
    return (DSAHandle)data_from_file(path);
}

DLLEXPORT void free_handle(DSAHandle h){
    if (!h) return;
    Data *d = (Data*)h;
    if (d->arr) free(d->arr);
    free(d);
}

DLLEXPORT int sort_by_roll(DSAHandle h){
    if (!h) return -1;
    Data *d = (Data*)h;
    qsort(d->arr, d->n, sizeof(Student), cmp_roll);
    return 0;
}

DLLEXPORT int sort_by_name(DSAHandle h){
    if (!h) return -1;
    Data *d = (Data*)h;
    qsort(d->arr, d->n, sizeof(Student), cmp_name);
    return 0;
}

DLLEXPORT int search_roll(DSAHandle h, int key, char* outbuf, size_t bufsz){
    if (!h || !outbuf) return -1;
    Data *d = (Data*)h;
    qsort(d->arr, d->n, sizeof(Student), cmp_roll);
    size_t lo = 0, hi = d->n;
    while (lo < hi){
        size_t mid = lo + (hi - lo)/2;
        if (d->arr[mid].roll == key){
            int wrote = snprintf(outbuf, bufsz, "%d,%s,%d", d->arr[mid].roll, d->arr[mid].name, d->arr[mid].marks);
            if (wrote < 0) return -1;
            return 0;
        } else if (d->arr[mid].roll < key) lo = mid + 1;
        else hi = mid;
    }
    return 1;
}

DLLEXPORT int stats(DSAHandle h, int* count, double* avg, int* minv, int* maxv){
    if (!h || !count || !avg || !minv || !maxv) return -1;
    Data *d = (Data*)h;
    if (d->n == 0){
        *count = 0; *avg = 0.0; *minv = 0; *maxv = 0;
        return 0;
    }
    long sum = 0;
    int mn = d->arr[0].marks;
    int mx = d->arr[0].marks;
    for (size_t i=0;i<d->n;i++){
        int m = d->arr[i].marks;
        sum += m;
        if (m < mn) mn = m;
        if (m > mx) mx = m;
    }
    *count = (int)d->n;
    *avg = (double)sum / (double)d->n;
    *minv = mn;
    *maxv = mx;
    return 0;
}

DLLEXPORT int export_to_string(DSAHandle h, char** outbuf, size_t* outlen){
    if (!h || !outbuf || !outlen) return -1;
    Data *d = (Data*)h;
    size_t est = d->n * (sizeof(Student) + 10);
    char *buf = malloc(est + 1);
    if (!buf) return -1;
    size_t used = 0;
    for (size_t i=0;i<d->n;i++){
        int needed = snprintf(NULL,0,"%d,%s,%d\n", d->arr[i].roll, d->arr[i].name, d->arr[i].marks);
        if (used + needed + 1 > est){
            est = (used + needed + 1) * 2;
            char *tmp = realloc(buf, est + 1);
            if (!tmp){ free(buf); return -1; }
            buf = tmp;
        }
        int wrote = snprintf(buf + used, est - used + 1, "%d,%s,%d\n", d->arr[i].roll, d->arr[i].name, d->arr[i].marks);
        if (wrote < 0){ free(buf); return -1; }
        used += (size_t)wrote;
    }
    buf[used] = '\0';
    *outbuf = buf;
    *outlen = used;
    return 0;
}

DLLEXPORT void free_string(char* s){
    if (s) free(s);
}

DLLEXPORT int export_to_file(DSAHandle h, const char* path){
    if (!h || !path) return -1;
    Data *d = (Data*)h;
    FILE *f = fopen(path, "w");
    if (!f) return -1;
    for (size_t i=0;i<d->n;i++){
        fprintf(f, "%d,%s,%d\n", d->arr[i].roll, d->arr[i].name, d->arr[i].marks);
    }
    fclose(f);
    return 0;
}

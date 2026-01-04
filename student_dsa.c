#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "student_dsa.h"

/*
 Usage:
  ./student_dsa action input.csv [output.csv] [key]
  actions:
    sort-roll      -> sorts by roll ascending, writes to output.csv or stdout
    sort-name      -> sorts by name lexicographically
    search-roll X  -> searches roll == X (requires input.csv), prints record if found
    stats          -> prints count, average marks, min, max
*/

#define LINE_BUFSZ 512

static int cmp_roll(const void *a, const void *b){
    const Student *pa = a;
    const Student *pb = b;
    return pa->roll - pb->roll;
}

static int cmp_name(const void *a, const void *b){
    const Student *pa = a;
    const Student *pb = b;
    return strcasecmp(pa->name, pb->name);
}

Student *read_csv(const char *path, size_t *out_n){
    FILE *f = fopen(path, "r");
    if (!f) return NULL;

    char line[LINE_BUFSZ];
    Student *arr = NULL;
    size_t cap = 0, n = 0;

    while (fgets(line, sizeof(line), f)) {
        if (line[0] == '\n' || line[0] == '\r') continue;

        // Expect CSV: roll,name,marks
        char *nl = strchr(line, '\n');
        if (nl) *nl = '\0';

        char *tok = strtok(line, ",");
        if (!tok) continue;
        int roll = atoi(tok);

        tok = strtok(NULL, ",");
        if (!tok) continue;
        char name[MAX_NAME_LEN];
        strncpy(name, tok, MAX_NAME_LEN - 1);
        name[MAX_NAME_LEN - 1] = '\0';

        tok = strtok(NULL, ",");
        if (!tok) continue;
        int marks = atoi(tok);

        if (n + 1 > cap) {
            cap = cap ? cap * 2 : 64;
            arr = realloc(arr, cap * sizeof(Student));
            if (!arr) { fclose(f); return NULL; }
        }

        arr[n].roll = roll;
        strncpy(arr[n].name, name, MAX_NAME_LEN - 1);
        arr[n].name[MAX_NAME_LEN - 1] = '\0';
        arr[n].marks = marks;
        n++;
    }

    fclose(f);
    *out_n = n;
    return arr;
}

/*
Student *read_csv(const char *path, size_t *out_n){
    FILE *f = fopen(path, "r");
    if (!f) return NULL;
    char line[LINE_BUFSZ];
    Student *arr = NULL;
    size_t cap = 0, n = 0;
    while (fgets(line, sizeof(line), f)){
        if (line[0] == '\n' || line[0]=='\r') continue;
        int roll = 0, marks = 0;
        char name[MAX_NAME_LEN] = {0};
        // Expect CSV: roll,name,marks
        char *p = line;
        // trim newline
        char *nl = strchr(p, '\n'); if (nl) *nl = 0;
        // parse
        char *tok = strtok(p, ",");
        if (!tok) continue;
        roll = atoi(tok);
        tok = strtok(NULL, ",");
        if (!tok) continue;
        strncpy(name, tok, MAX_NAME_LEN-1);
        tok = strtok(NULL, ",");
        if (!tok) continue;
        marks = atoi(tok);

        if (n + 1 > cap){
            cap = cap ? cap * 2 : 64;
            arr = realloc(arr, cap * sizeof(Student));
            if (!arr){ fclose(f); return NULL; }
        }
        arr[n].roll = roll;
        strncpy(arr[n].name, name, MAX_NAME_LEN-1);
        arr[n].name[MAX_NAME_LEN - 1] = '\0';
        //arr[n].marks = marks;
        n++;
    }
    fclose(f);
    *out_n = n;
    return arr;
}
*/
void write_csv_to_file(const Student *arr, size_t n, const char *outpath){
    FILE *f = outpath ? fopen(outpath, "w") : stdout;
    if (!f) return;
    for (size_t i=0;i<n;i++){
        fprintf(f, "%d,%s,%d\n", arr[i].roll, arr[i].name, arr[i].marks);
    }
    if (outpath) fclose(f);
}

int main(int argc, char **argv){
    if (argc < 3){
        fprintf(stderr, "Usage: %s action input.csv [output.csv] [key]\n", argv[0]);
        return 2;
    }
    const char *action = argv[1];
    const char *input = argv[2];
    const char *output = NULL;
    if (argc >= 4) output = argv[3];

    size_t n = 0;
    Student *arr = read_csv(input, &n);
    if (!arr){
        fprintf(stderr, "Failed to read input csv '%s'\n", input);
        return 3;
    }

    if (strcmp(action, "sort-roll") == 0){
        qsort(arr, n, sizeof(Student), cmp_roll);
        write_csv_to_file(arr, n, output);
    } else if (strcmp(action, "sort-name") == 0){
        qsort(arr, n, sizeof(Student), cmp_name);
        write_csv_to_file(arr, n, output);
    } else if (strcmp(action, "search-roll") == 0){
        if (argc < 4){
            fprintf(stderr, "search-roll requires a key\n");
            free(arr); return 4;
        }
        int key = atoi(argv[3]);
        // ensure sorted by roll for binary search
        qsort(arr, n, sizeof(Student), cmp_roll);
        size_t lo = 0, hi = n;
        while (lo < hi){
            size_t mid = lo + (hi - lo)/2;
            if (arr[mid].roll == key){
                printf("%d,%s,%d\n", arr[mid].roll, arr[mid].name, arr[mid].marks);
                free(arr);
                return 0;
            } else if (arr[mid].roll < key){
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        // not found
        return 5;
    } else if (strcmp(action, "stats") == 0){
        if (n == 0){ printf("count,0\navg,0\nmin,0\nmax,0\n"); free(arr); return 0; }
        long sum = 0; int mn = arr[0].marks, mx = arr[0].marks;
        for (size_t i=0;i<n;i++){
            sum += arr[i].marks;
            if (arr[i].marks < mn) mn = arr[i].marks;
            if (arr[i].marks > mx) mx = arr[i].marks;
        }
        double avg = (double)sum / (double)n;
        printf("count,%zu\navg,%.2f\nmin,%d\nmax,%d\n", n, avg, mn, mx);
    } else {
        fprintf(stderr, "Unknown action: %s\n", action);
        free(arr);
        return 6;
    }

    free(arr);
    return 0;
}

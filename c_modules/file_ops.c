/*
 * file_ops.c — File I/O implementation (binary + CSV)
 * Student Record Management System
 */

#include "file_ops.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ══════════════════════════════════════════════════════════════════════════
   BINARY  FORMAT
   Header: [magic:4][version:4][count:4]
   Records: n × sizeof(Student)
   ══════════════════════════════════════════════════════════════════════════ */

int file_save_binary(const char *path, const Student *arr, int n) {
    FILE *fp = fopen(path, "wb");
    if (!fp) { perror("[FILE] fopen"); return -1; }

    unsigned int magic = BINARY_MAGIC, ver = BINARY_VER, cnt = (unsigned int)n;
    fwrite(&magic, sizeof(magic), 1, fp);
    fwrite(&ver,   sizeof(ver),   1, fp);
    fwrite(&cnt,   sizeof(cnt),   1, fp);
    fwrite(arr, sizeof(Student), n, fp);
    fclose(fp);
    printf("[FILE] Saved %d records → %s\n", n, path);
    return 0;
}

int file_load_binary(const char *path, Student *arr, int capacity) {
    FILE *fp = fopen(path, "rb");
    if (!fp) { perror("[FILE] fopen"); return -1; }

    unsigned int magic, ver, cnt;
    if (fread(&magic, sizeof(magic), 1, fp) != 1 || magic != BINARY_MAGIC) {
        fprintf(stderr, "[FILE] Invalid file format: %s\n", path);
        fclose(fp); return -1;
    }
    fread(&ver, sizeof(ver), 1, fp);
    fread(&cnt, sizeof(cnt), 1, fp);

    int to_read = (int)cnt < capacity ? (int)cnt : capacity;
    int read    = (int)fread(arr, sizeof(Student), to_read, fp);
    fclose(fp);
    printf("[FILE] Loaded %d/%d records ← %s\n", read, (int)cnt, path);
    return read;
}

/* ── count records without loading all ──────────────────────────────────── */
int file_count_records(const char *path) {
    FILE *fp = fopen(path, "rb");
    if (!fp) return -1;
    unsigned int magic, ver, cnt;
    fread(&magic, sizeof(magic), 1, fp);
    fread(&ver,   sizeof(ver),   1, fp);
    fread(&cnt,   sizeof(cnt),   1, fp);
    fclose(fp);
    return (magic == BINARY_MAGIC) ? (int)cnt : -1;
}

/* ── append single record (rewrite header count) ────────────────────────── */
int file_append_record(const char *path, const Student *s) {
    /* load existing */
    int existing = file_count_records(path);
    if (existing < 0) existing = 0;

    Student *buf = (Student *)malloc((existing + 1) * sizeof(Student));
    if (!buf) return -1;

    if (existing > 0) file_load_binary(path, buf, existing);
    student_copy(&buf[existing], s);
    int rc = file_save_binary(path, buf, existing + 1);
    free(buf);
    return rc;
}

/* ── copy a file ────────────────────────────────────────────────────────── */
int file_backup(const char *src, const char *dst) {
    FILE *in  = fopen(src, "rb");
    FILE *out = fopen(dst, "wb");
    if (!in || !out) {
        if (in)  fclose(in);
        if (out) fclose(out);
        return -1;
    }
    char buf[4096];
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), in)) > 0)
        fwrite(buf, 1, n, out);
    fclose(in); fclose(out);
    printf("[FILE] Backup: %s → %s\n", src, dst);
    return 0;
}

/* ══════════════════════════════════════════════════════════════════════════
   CSV  FORMAT
   Line 0: header row
   Line 1+: id,code,first_name,last_name,email,phone,department,status,gpa
   ══════════════════════════════════════════════════════════════════════════ */

int file_save_csv(const char *path, const Student *arr, int n) {
    FILE *fp = fopen(path, "w");
    if (!fp) { perror("[FILE] fopen"); return -1; }

    fprintf(fp, "student_id,student_code,first_name,last_name,"
                "email,phone,department,status,gpa\n");
    for (int i = 0; i < n; i++) {
        const Student *s = &arr[i];
        fprintf(fp, "%d,%s,%s,%s,%s,%s,%s,%s,%.2f\n",
                s->student_id, s->student_code,
                s->first_name, s->last_name,
                s->email, s->phone,
                s->department, s->status, s->gpa);
    }
    fclose(fp);
    printf("[FILE] CSV saved %d records → %s\n", n, path);
    return 0;
}

int file_load_csv(const char *path, Student *arr, int capacity) {
    FILE *fp = fopen(path, "r");
    if (!fp) { perror("[FILE] fopen"); return -1; }

    char line[512];
    fgets(line, sizeof(line), fp);   /* skip header */

    int count = 0;
    while (count < capacity && fgets(line, sizeof(line), fp)) {
        Student *s = &arr[count];
        /* parse CSV line */
        char *tok = strtok(line, ",");
        if (!tok) continue;
        s->student_id = atoi(tok);

        #define NEXT_FIELD(dst, sz) \
            tok = strtok(NULL, ","); \
            if (tok) { strncpy(dst, tok, sz - 1); dst[sz-1] = '\0'; }

        NEXT_FIELD(s->student_code, MAX_CODE)
        NEXT_FIELD(s->first_name,   MAX_NAME)
        NEXT_FIELD(s->last_name,    MAX_NAME)
        NEXT_FIELD(s->email,        MAX_EMAIL)
        NEXT_FIELD(s->phone,        MAX_PHONE)
        NEXT_FIELD(s->department,   MAX_DEPT)
        NEXT_FIELD(s->status,       MAX_STATUS)

        tok = strtok(NULL, ",\n");
        if (tok) s->gpa = (float)atof(tok);

        #undef NEXT_FIELD
        count++;
    }
    fclose(fp);
    printf("[FILE] CSV loaded %d records ← %s\n", count, path);
    return count;
}

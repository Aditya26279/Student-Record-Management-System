/*
 * file_ops.h — File I/O for persisting Student records (binary + CSV)
 * Student Record Management System
 */

#ifndef FILE_OPS_H
#define FILE_OPS_H

#include "student.h"

#define BINARY_MAGIC  0x53524D53u  /* "SRMS" */
#define BINARY_VER    1

/* ── Binary file format ──────────────────────────────────────────────────── */
/* Header: magic(4) + version(4) + count(4) = 12 bytes, followed by records */

int  file_save_binary(const char *path, const Student *arr, int n);
int  file_load_binary(const char *path, Student *arr, int capacity);

/* ── CSV file format ─────────────────────────────────────────────────────── */
/* id,code,first_name,last_name,email,phone,department,status,gpa          */
int  file_save_csv(const char *path, const Student *arr, int n);
int  file_load_csv(const char *path, Student *arr, int capacity);

/* ── Utility ──────────────────────────────────────────────────────────────── */
int  file_count_records(const char *path);  /* binary file */
int  file_append_record(const char *path, const Student *s);
int  file_backup(const char *src, const char *dst);

#endif /* FILE_OPS_H */

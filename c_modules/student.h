/*
 * student.h — Shared Student structure used across all C modules
 * Student Record Management System
 */

#ifndef STUDENT_H
#define STUDENT_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ─── Constants ─────────────────────────────────────────────────────────── */
#define MAX_NAME    50
#define MAX_CODE    20
#define MAX_EMAIL   100
#define MAX_PHONE   15
#define MAX_DEPT    60
#define MAX_STATUS  15

/* ─── Student record ────────────────────────────────────────────────────── */
typedef struct {
    int    student_id;
    char   student_code[MAX_CODE];
    char   first_name[MAX_NAME];
    char   last_name[MAX_NAME];
    char   email[MAX_EMAIL];
    char   phone[MAX_PHONE];
    char   department[MAX_DEPT];
    char   status[MAX_STATUS];   /* active | inactive | graduated */
    float  gpa;
} Student;

/* ─── Utility ────────────────────────────────────────────────────────────── */
static inline void student_print(const Student *s) {
    printf("  [%d] %s %s | Code: %-12s | GPA: %.2f | Dept: %s | Status: %s\n",
           s->student_id, s->first_name, s->last_name,
           s->student_code, s->gpa, s->department, s->status);
}

static inline void student_copy(Student *dst, const Student *src) {
    memcpy(dst, src, sizeof(Student));
}

#endif /* STUDENT_H */

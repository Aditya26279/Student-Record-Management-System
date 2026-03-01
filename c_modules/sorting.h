/*
 * sorting.h — Sorting algorithms for Student arrays
 * Student Record Management System
 */

#ifndef SORTING_H
#define SORTING_H

#include "student.h"

/* Comparator function type — returns <0, 0, >0 */
typedef int (*StudentCmp)(const Student *a, const Student *b);

/* ── Predefined comparators ─────────────────────────────────────────────── */
int cmp_by_id        (const Student *a, const Student *b);
int cmp_by_name      (const Student *a, const Student *b);  /* last, first */
int cmp_by_gpa_desc  (const Student *a, const Student *b);  /* highest first */
int cmp_by_dept      (const Student *a, const Student *b);

/* ── Sorting algorithms ──────────────────────────────────────────────────── */
void bubble_sort (Student *arr, int n, StudentCmp cmp);
void selection_sort(Student *arr, int n, StudentCmp cmp);
void insertion_sort(Student *arr, int n, StudentCmp cmp);
void merge_sort  (Student *arr, int n, StudentCmp cmp);
void quick_sort  (Student *arr, int n, StudentCmp cmp);

/* Measure time (seconds) for any sort function */
double sort_benchmark(void (*sort_fn)(Student *, int, StudentCmp),
                      Student *arr, int n, StudentCmp cmp);

#endif /* SORTING_H */

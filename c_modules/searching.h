/*
 * searching.h — Search algorithms on sorted Student arrays
 * Student Record Management System
 */

#ifndef SEARCHING_H
#define SEARCHING_H

#include "student.h"
#include "sorting.h"   /* for StudentCmp */

/* ── Search algorithms ───────────────────────────────────────────────────── */

/* Linear search — O(n), works on any array */
int linear_search_by_id   (const Student *arr, int n, int id);
int linear_search_by_name (const Student *arr, int n, const char *name);

/* Binary search — O(log n), array must be sorted by student_id */
int binary_search_by_id   (const Student *arr, int n, int id);

/* Binary search by GPA — array must be sorted descending by GPA */
int binary_search_by_gpa  (const Student *arr, int n, float gpa);

/* Find all students matching a department (sorted by dept) */
int find_by_department(const Student *arr, int n,
                       const char *dept, int *indices, int max_indices);

/* Find students within a GPA range [lo, hi] */
int find_by_gpa_range(const Student *arr, int n,
                      float lo, float hi, Student *out, int max_out);

#endif /* SEARCHING_H */

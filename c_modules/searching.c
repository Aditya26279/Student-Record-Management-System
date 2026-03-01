/*
 * searching.c — Search algorithm implementations
 * Student Record Management System
 */

#include "searching.h"
#include <stdio.h>
#include <string.h>

/* ══════════════════════════════════════════════════════════════════════════
   LINEAR SEARCH  —  O(n)
   ══════════════════════════════════════════════════════════════════════════ */

/* Returns index, or -1 if not found */
int linear_search_by_id(const Student *arr, int n, int id) {
    for (int i = 0; i < n; i++)
        if (arr[i].student_id == id) return i;
    return -1;
}

/* Case-insensitive partial match on first_name OR last_name */
int linear_search_by_name(const Student *arr, int n, const char *name) {
    char lower_name[MAX_NAME], lower_first[MAX_NAME], lower_last[MAX_NAME];

    /* lower-case the query */
    int qi = 0;
    while (name[qi]) { lower_name[qi] = (char)(name[qi] | 32); qi++; }
    lower_name[qi] = '\0';

    for (int i = 0; i < n; i++) {
        int fi = 0, li = 0;
        while (arr[i].first_name[fi]) {
            lower_first[fi] = (char)(arr[i].first_name[fi] | 32); fi++;
        }
        lower_first[fi] = '\0';
        while (arr[i].last_name[li]) {
            lower_last[li] = (char)(arr[i].last_name[li] | 32); li++;
        }
        lower_last[li] = '\0';

        if (strstr(lower_first, lower_name) || strstr(lower_last, lower_name))
            return i;
    }
    return -1;
}

/* ══════════════════════════════════════════════════════════════════════════
   BINARY SEARCH by student_id  —  O(log n)
   Array must be sorted ascending by student_id.
   ══════════════════════════════════════════════════════════════════════════ */
int binary_search_by_id(const Student *arr, int n, int id) {
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if      (arr[mid].student_id == id) return mid;
        else if (arr[mid].student_id <  id) lo = mid + 1;
        else                                hi = mid - 1;
    }
    return -1;
}

/* ══════════════════════════════════════════════════════════════════════════
   BINARY SEARCH by GPA  —  O(log n)
   Array must be sorted descending by GPA.
   Returns first index with gpa == target or -1.
   ══════════════════════════════════════════════════════════════════════════ */
int binary_search_by_gpa(const Student *arr, int n, float gpa) {
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        float mg = arr[mid].gpa;
        if      (mg == gpa) return mid;
        else if (mg >  gpa) lo = mid + 1;  /* descending */
        else                hi = mid - 1;
    }
    return -1;
}

/* ══════════════════════════════════════════════════════════════════════════
   FIND BY DEPARTMENT  —  O(n)
   Stores matching indices into 'indices'. Returns count found.
   ══════════════════════════════════════════════════════════════════════════ */
int find_by_department(const Student *arr, int n,
                       const char *dept, int *indices, int max_indices) {
    int count = 0;
    for (int i = 0; i < n && count < max_indices; i++) {
        if (strcmp(arr[i].department, dept) == 0)
            indices[count++] = i;
    }
    return count;
}

/* ══════════════════════════════════════════════════════════════════════════
   FIND BY GPA RANGE  —  O(n)
   Returns students with gpa in [lo, hi] into 'out'. Returns count.
   ══════════════════════════════════════════════════════════════════════════ */
int find_by_gpa_range(const Student *arr, int n,
                      float lo, float hi, Student *out, int max_out) {
    int count = 0;
    for (int i = 0; i < n && count < max_out; i++) {
        if (arr[i].gpa >= lo && arr[i].gpa <= hi)
            student_copy(&out[count++], &arr[i]);
    }
    return count;
}

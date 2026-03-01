/*
 * sorting.c — Sorting algorithm implementations
 * Student Record Management System
 */

#include "sorting.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* ── Comparators ────────────────────────────────────────────────────────── */
int cmp_by_id(const Student *a, const Student *b) {
    return a->student_id - b->student_id;
}

int cmp_by_name(const Student *a, const Student *b) {
    int r = strcmp(a->last_name, b->last_name);
    return (r != 0) ? r : strcmp(a->first_name, b->first_name);
}

int cmp_by_gpa_desc(const Student *a, const Student *b) {
    if (b->gpa > a->gpa) return  1;
    if (b->gpa < a->gpa) return -1;
    return 0;
}

int cmp_by_dept(const Student *a, const Student *b) {
    return strcmp(a->department, b->department);
}

/* ── Helper: swap two students ──────────────────────────────────────────── */
static void swap(Student *a, Student *b) {
    Student tmp;
    student_copy(&tmp, a);
    student_copy(a, b);
    student_copy(b, &tmp);
}

/* ══════════════════════════════════════════════════════════════════════════
   BUBBLE SORT  —  O(n²), stable
   ══════════════════════════════════════════════════════════════════════════ */
void bubble_sort(Student *arr, int n, StudentCmp cmp) {
    for (int i = 0; i < n - 1; i++) {
        int swapped = 0;
        for (int j = 0; j < n - i - 1; j++) {
            if (cmp(&arr[j], &arr[j + 1]) > 0) {
                swap(&arr[j], &arr[j + 1]);
                swapped = 1;
            }
        }
        if (!swapped) break;  /* already sorted */
    }
}

/* ══════════════════════════════════════════════════════════════════════════
   SELECTION SORT  —  O(n²), not stable
   ══════════════════════════════════════════════════════════════════════════ */
void selection_sort(Student *arr, int n, StudentCmp cmp) {
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) {
            if (cmp(&arr[j], &arr[min_idx]) < 0) min_idx = j;
        }
        if (min_idx != i) swap(&arr[i], &arr[min_idx]);
    }
}

/* ══════════════════════════════════════════════════════════════════════════
   INSERTION SORT  —  O(n²) worst, O(n) best, stable
   ══════════════════════════════════════════════════════════════════════════ */
void insertion_sort(Student *arr, int n, StudentCmp cmp) {
    for (int i = 1; i < n; i++) {
        Student key;
        student_copy(&key, &arr[i]);
        int j = i - 1;
        while (j >= 0 && cmp(&arr[j], &key) > 0) {
            student_copy(&arr[j + 1], &arr[j]);
            j--;
        }
        student_copy(&arr[j + 1], &key);
    }
}

/* ══════════════════════════════════════════════════════════════════════════
   MERGE SORT  —  O(n log n), stable
   ══════════════════════════════════════════════════════════════════════════ */
static void merge(Student *arr, int lo, int mid, int hi, StudentCmp cmp) {
    int ln = mid - lo + 1, rn = hi - mid;
    Student *L = (Student *)malloc(ln * sizeof(Student));
    Student *R = (Student *)malloc(rn * sizeof(Student));
    if (!L || !R) { free(L); free(R); return; }

    for (int i = 0; i < ln; i++) student_copy(&L[i], &arr[lo + i]);
    for (int j = 0; j < rn; j++) student_copy(&R[j], &arr[mid + 1 + j]);

    int i = 0, j = 0, k = lo;
    while (i < ln && j < rn) {
        if (cmp(&L[i], &R[j]) <= 0) student_copy(&arr[k++], &L[i++]);
        else                         student_copy(&arr[k++], &R[j++]);
    }
    while (i < ln) student_copy(&arr[k++], &L[i++]);
    while (j < rn) student_copy(&arr[k++], &R[j++]);
    free(L); free(R);
}

static void merge_r(Student *arr, int lo, int hi, StudentCmp cmp) {
    if (lo >= hi) return;
    int mid = lo + (hi - lo) / 2;
    merge_r(arr, lo,      mid, cmp);
    merge_r(arr, mid + 1, hi,  cmp);
    merge(arr, lo, mid, hi, cmp);
}

void merge_sort(Student *arr, int n, StudentCmp cmp) {
    if (n > 1) merge_r(arr, 0, n - 1, cmp);
}

/* ══════════════════════════════════════════════════════════════════════════
   QUICK SORT  —  O(n log n) avg, O(n²) worst, median-of-three pivot
   ══════════════════════════════════════════════════════════════════════════ */
static int median_of_three(Student *arr, int lo, int hi, StudentCmp cmp) {
    int mid = lo + (hi - lo) / 2;
    if (cmp(&arr[lo],  &arr[mid]) > 0) swap(&arr[lo],  &arr[mid]);
    if (cmp(&arr[lo],  &arr[hi])  > 0) swap(&arr[lo],  &arr[hi]);
    if (cmp(&arr[mid], &arr[hi])  > 0) swap(&arr[mid], &arr[hi]);
    swap(&arr[mid], &arr[hi - 1]);
    return hi - 1;   /* pivot index */
}

static void quick_r(Student *arr, int lo, int hi, StudentCmp cmp) {
    if (hi - lo < 10) { /* fall back to insertion for small partitions */
        insertion_sort(arr + lo, hi - lo + 1, cmp);
        return;
    }
    int pi = median_of_three(arr, lo, hi, cmp);
    Student pivot;
    student_copy(&pivot, &arr[pi]);

    int i = lo, j = hi - 1;
    for (;;) {
        while (cmp(&arr[++i], &pivot) < 0);
        while (cmp(&arr[--j], &pivot) > 0);
        if (i >= j) break;
        swap(&arr[i], &arr[j]);
    }
    swap(&arr[i], &arr[hi - 1]);

    quick_r(arr, lo,    i - 1, cmp);
    quick_r(arr, i + 1, hi,    cmp);
}

void quick_sort(Student *arr, int n, StudentCmp cmp) {
    if (n > 1) quick_r(arr, 0, n - 1, cmp);
}

/* ── Benchmark helper ───────────────────────────────────────────────────── */
double sort_benchmark(void (*sort_fn)(Student *, int, StudentCmp),
                      Student *arr, int n, StudentCmp cmp) {
    /* Work on a copy so caller's array is unchanged */
    Student *copy = (Student *)malloc(n * sizeof(Student));
    if (!copy) return -1.0;
    for (int i = 0; i < n; i++) student_copy(&copy[i], &arr[i]);

    clock_t start = clock();
    sort_fn(copy, n, cmp);
    clock_t end   = clock();

    free(copy);
    return (double)(end - start) / CLOCKS_PER_SEC;
}

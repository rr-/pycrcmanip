#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *CrcNext(PyObject *self, PyObject *args) {
    char *str = NULL;
    Py_ssize_t strsize = 0;
    uint32_t value = 0;
    PyObject *crc;

    if (!PyArg_ParseTuple(args, "Oy#I", &crc, &str, &strsize, &value)) {
        return NULL;
    }

    const int num_bytes = PyLong_AsLong(
        PyObject_GetAttrString(crc, "num_bytes")
    );
    const int num_bits = PyLong_AsLong(
        PyObject_GetAttrString(crc, "num_bits")
    );
    const int big_endian = PyObject_IsTrue(
        PyObject_GetAttrString(crc, "big_endian")
    );
    uint32_t lookup_table[256] = {0};
    PyObject *py_lookup_table = PyObject_GetAttrString(crc, "lookup_table");
    if (!py_lookup_table) {
        return NULL;
    }
    for (int i = 0; i < 256; i++) {
        lookup_table[i] = PyLong_AsLong(PyTuple_GetItem(py_lookup_table, i));
    }

    const uint32_t mask = (1ull << num_bits) - 1ull;
    int shift = (num_bytes << 3) - 8;
    if (big_endian) {
        for (int i = 0; i < strsize; i++) {
            uint8_t c = *str++;
            uint8_t index = c ^ (value >> shift);
            value = lookup_table[index] ^ (value << 8);
            value &= mask;
        }
    } else {
        for (int i = 0; i < strsize; i++) {
            uint8_t c = *str++;
            uint8_t index = c ^ value;
            value = lookup_table[index] ^ (value >> 8);
            value &= mask;
        }
    }

    return PyLong_FromLong(value);
}

static PyObject *CrcPrev(PyObject *self, PyObject *args) {
    char *str = NULL;
    Py_ssize_t strsize = 0;
    uint32_t value = 0;
    PyObject *crc;

    if (!PyArg_ParseTuple(args, "Oy#I", &crc, &str, &strsize, &value)) {
        return NULL;
    }

    const int num_bytes = PyLong_AsLong(
        PyObject_GetAttrString(crc, "num_bytes")
    );
    const int num_bits = PyLong_AsLong(
        PyObject_GetAttrString(crc, "num_bits")
    );
    const int big_endian = PyObject_IsTrue(
        PyObject_GetAttrString(crc, "big_endian")
    );
    uint32_t lookup_table_reverse[256] = {0};
    PyObject *py_lookup_table_reverse = PyObject_GetAttrString(
        crc, "lookup_table_reverse"
    );
    if (!py_lookup_table_reverse) {
        return NULL;
    }
    for (int i = 0; i < 256; i++) {
        lookup_table_reverse[i] = PyLong_AsLong(
            PyTuple_GetItem(py_lookup_table_reverse, i)
        );
    }

    const uint32_t mask = (1ull << num_bits) - 1ull;
    str += strsize - 1;
    int shift = (num_bytes << 3) - 8;
    if (big_endian) {
        for (int i = 0; i < strsize; i++) {
            uint8_t c = *str--;
            uint8_t index = value;
            value = (
                (c << shift)
                ^ lookup_table_reverse[index]
                ^ (value << shift)
                ^ (value >> 8)
            );
            value &= mask;
        }
    } else {
        for (int i = 0; i < strsize; i++) {
            uint8_t c = *str--;
            uint8_t index = value >> shift;
            value = c ^ lookup_table_reverse[index] ^ (value << 8);
            value &= mask;
        }
    }
    return PyLong_FromLong(value);
}

static PyMethodDef FastCrcMethods[] = {
    {"crc_next", CrcNext, METH_VARARGS, "crc_next"},
    {"crc_prev", CrcPrev, METH_VARARGS, "crc_prev"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef fastcrcmodule = {
    PyModuleDef_HEAD_INIT,
    "crcmanip.fastcrc",
    "Python interface for the crcmanip.fastcrc C library functions",
    -1,
    FastCrcMethods
};

PyMODINIT_FUNC PyInit_fastcrc(void) {
    return PyModule_Create(&fastcrcmodule);
}

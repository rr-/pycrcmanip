#include <Python.h>

static PyObject *CrcNext(PyObject *self, PyObject *args) {
    char *str = NULL;
    size_t strsize = 0;
    uint32_t value = 0;
    PyObject *crc;

    if (!PyArg_ParseTuple(args, "Oy#I", &crc, &str, &strsize, &value)) {
        return NULL;
    }

    const size_t num_bytes = PyLong_AsLong(
        PyObject_GetAttrString(crc, "num_bytes")
    );
    const size_t num_bits = PyLong_AsLong(
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
    for (int i = 0; i < strsize; i++) {
        uint8_t c = *str++;
        if (big_endian) {
            uint8_t index = (value >> (num_bytes * 8 - 8)) ^ c;
            value = lookup_table[index] ^ (value << 8);
        } else {
            uint8_t index = c ^ value;
            value = lookup_table[index] ^ (value >> 8);
        }
        value &= mask;
    }

    return PyLong_FromLong(value);
}

static PyObject *CrcPrev(PyObject *self, PyObject *args) {
    char *str = NULL;
    size_t strsize = 0;
    uint32_t value = 0;
    PyObject *crc;

    if (!PyArg_ParseTuple(args, "Oy#I", &crc, &str, &strsize, &value)) {
        return NULL;
    }

    const size_t num_bytes = PyLong_AsLong(
        PyObject_GetAttrString(crc, "num_bytes")
    );
    const size_t num_bits = PyLong_AsLong(
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
    str += strsize;
    for (int i = 0; i < strsize; i++) {
        uint8_t c = *--str;
        if (big_endian) {
            uint8_t index = value & 0xFF;
            value = (
                (c << (num_bytes * 8 - 8))
                ^ lookup_table_reverse[index]
                ^ (value << (num_bytes * 8 - 8))
                ^ (value >> 8)
            ) & mask;
        } else {
            uint8_t index = value >> (num_bytes * 8 - 8);
            value = (
                (value << 8) ^ lookup_table_reverse[index] ^ c
            ) & mask;
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

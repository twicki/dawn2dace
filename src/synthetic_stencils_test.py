import unittest
import numpy
import sys
import os

# This is a workaround for a bug in vscode. Apparently it ignores PYTHONPATH. (6.Nov 2019)
sys.path.append(os.path.relpath("build/gen/iir_specification/"))
sys.path.append(os.path.relpath("../dace"))

import dawn2dace
import dace

def read_file(file_name):
    with open("gen/" + file_name, "rb") as f:
        return f.read() # IIR as binary str.
    return None

def get_sdfg(file_name):
    iir = read_file(file_name)
    return dawn2dace.IIR_str_to_SDFG(iir)

class LegalSDFG:
    def test_file_exists(self):
        self.assertIsNotNone(read_file(self.file_name))

    def test_sdfg_is_valid(self):
        sdfg = get_sdfg(self.file_name)
        self.assertTrue(sdfg.is_valid())
        

class copy(LegalSDFG, unittest.TestCase):
    file_name = "copy.0.iir"

    def test_numerically(self):
        I,J,K = 3,3,3
        halo_size = 0
        input = numpy.arange(J*K*I).astype(dace.float64.type).reshape(J,K,I)
        output = numpy.zeros(shape=(J,K,I), dtype=dace.float64.type)
        
        sdfg = get_sdfg(self.file_name)
        sdfg = sdfg.compile(optimizer="")

        sdfg(
            data_in_t = input,
            data_out_t = output,
            I = numpy.int32(I),
            J = numpy.int32(J),
            K = numpy.int32(K),
            halo_size = numpy.int32(halo_size))

        self.assertTrue((input == output).all(), "Expected:\n{}\nReceived:\n{}".format(input, output))


class inout_variable(LegalSDFG, unittest.TestCase):
    file_name = "inout_variable.0.iir"

    def test_numerically(self):
        I,J,K = 3,3,3
        halo_size = 0
        in_out = numpy.zeros(shape=(J,K,I), dtype=dace.float64.type)
        expected = in_out + 7
        
        sdfg = get_sdfg(self.file_name)
        sdfg = sdfg.compile(optimizer="")

        sdfg(
            a_t = in_out,
            I = numpy.int32(I),
            J = numpy.int32(J),
            K = numpy.int32(K),
            halo_size = numpy.int32(halo_size))

        self.assertTrue((in_out == expected).all(), "Expected:\n{}\nReceived:\n{}".format(expected, in_out))


class offsets(LegalSDFG, unittest.TestCase):
    file_name = "offsets.0.iir"

    def test_numerically(self):
        I,J,K = 3,3,3
        halo_size = 1
        input = numpy.arange(J*K*I).astype(dace.float64.type).reshape(J,K,I)
        output = numpy.zeros(shape=(J,K,I), dtype=dace.float64.type)

        expected = numpy.copy(output)
        for k in range(0, K):
            expected[1, k, 1] = input[1-1, k, 1+1] + input[1, k, 1-1]
        
        # a = b[i + 1, j - 1] + b[i - 1];
        sdfg = get_sdfg(self.file_name)
        sdfg = sdfg.compile(optimizer="")

        sdfg(
            b_t = input,
            a_t = output,
            I = numpy.int32(I),
            J = numpy.int32(J),
            K = numpy.int32(K),
            halo_size = numpy.int32(halo_size))

        self.assertTrue((output == expected).all(), "Expected:\n{}\nReceived:\n{}".format(expected, output))


class vertical_specification(LegalSDFG, unittest.TestCase):
    file_name = "vertical_specification.0.iir"

    def test_numerically(self):
        I,J,K = 4,4,4
        halo_size = 0
        input1 = numpy.arange(J*K*I).astype(dace.float64.type).reshape(J,K,I)
        input2 = numpy.arange(J*K*I).astype(dace.float64.type).reshape(J,K,I)
        output = numpy.zeros(shape=(J,K,I), dtype=dace.float64.type)

        expected = numpy.copy(input2)
        for k in range(3, K):
            expected[:, k, :] = input1[:, k, :]
        
        sdfg = get_sdfg(self.file_name)
        sdfg = sdfg.compile(optimizer="")

        sdfg(
            data_in_1_t = input1,
            data_in_2_t = input2,
            data_out_t = output,
            I = numpy.int32(I),
            J = numpy.int32(J),
            K = numpy.int32(K),
            halo_size = numpy.int32(halo_size))

        self.assertTrue((output == expected).all(), "Expected:\n{}\nReceived:\n{}".format(expected, output))


class vertical_offsets(LegalSDFG, unittest.TestCase):
    file_name = "vertical_offsets.0.iir"

    def test_numerically(self):
        I,J,K = 3,3,3
        halo_size = 0
        input = numpy.arange(J*K*I).astype(dace.float64.type).reshape(J,K,I)
        output = numpy.zeros(shape=(J,K,I), dtype=dace.float64.type)

        expected = numpy.copy(output)

        # vertical_region(k_start, k_start) { out_field = in_field }
        expected[:, 0, :] = input[:, 0, :]

        # vertical_region(k_start + 1, k_end) { out_field = in_field[k - 1]; }
        for k in range(1, K):
            expected[:, k, :] = input[:, k-1, :]
        
        sdfg = get_sdfg(self.file_name)
        sdfg = sdfg.compile(optimizer="")

        sdfg(
            in_field_t = input,
            out_field_t = output,
            I = numpy.int32(I),
            J = numpy.int32(J),
            K = numpy.int32(K),
            halo_size = numpy.int32(halo_size))

        self.assertTrue((output == expected).all(), "Expected:\n{}\nReceived:\n{}".format(expected, output))


class local_variables(LegalSDFG, unittest.TestCase):
    file_name = "local_variables.0.iir"

    def test_numerically(self):
        I,J,K = 3,3,3
        halo_size = 0
        input = numpy.arange(J*K*I).astype(dace.float64.type).reshape(J,K,I)
        output = numpy.zeros(shape=(J,K,I), dtype=dace.float64.type)

        expected = input + 5
        
        sdfg = get_sdfg(self.file_name)
        sdfg = sdfg.compile(optimizer="")

        sdfg(
            in_field_t = input,
            out_field_t = output,
            I = numpy.int32(I),
            J = numpy.int32(J),
            K = numpy.int32(K),
            halo_size = numpy.int32(halo_size))

        self.assertTrue((output == expected).all(), "Expected:\n{}\nReceived:\n{}".format(expected, output))


class local_internal(LegalSDFG, unittest.TestCase):
    file_name = "local_internal.0.iir"

    def test_numerically(self):
        I,J,K = 3,3,3
        halo_size = 0
        input = numpy.arange(J*K*I).astype(dace.float64.type).reshape(J,K,I)
        output = numpy.zeros(shape=(J,K,I), dtype=dace.float64.type)

        expected = input + 5
        
        sdfg = get_sdfg(self.file_name)
        sdfg = sdfg.compile(optimizer="")

        sdfg(
            in_field_t = input,
            out_field_t = output,
            I = numpy.int32(I),
            J = numpy.int32(J),
            K = numpy.int32(K),
            halo_size = numpy.int32(halo_size))

        self.assertTrue((output == expected).all(), "Expected:\n{}\nReceived:\n{}".format(expected, output))


class brackets(LegalSDFG, unittest.TestCase):
    file_name = "brackets.0.iir"

    def test_numerically(self):
        I,J,K = 3,3,3
        halo_size = 0
        input = numpy.arange(J*K*I).astype(dace.float64.type).reshape(J,K,I)
        output = numpy.zeros(shape=(J,K,I), dtype=dace.float64.type)

        # out_field = 0.25 * (in_field + 7);
        expected = 0.25 * (input + 7)
        
        sdfg = get_sdfg(self.file_name)
        sdfg = sdfg.compile(optimizer="")

        sdfg(
            in_field_t = input,
            out_field_t = output,
            I = numpy.int32(I),
            J = numpy.int32(J),
            K = numpy.int32(K),
            halo_size = numpy.int32(halo_size))

        self.assertTrue((output == expected).all(), "Expected:\n{}\nReceived:\n{}".format(expected, output))


if __name__ == '__main__':
    unittest.main()
    
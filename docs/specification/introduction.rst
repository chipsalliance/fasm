.. _Specification:Introduction:

Introduction
------------

The FASM is a file format designed to specify the bits in an FPGA bitstream that need to be set (e.g. binary 1) or
cleared (e.g. binary 0).

A FASM file declares that specific "Features" within the bitstream should be enabled.
Enabling a feature will cause bits within the bitstream to be set or cleared.

A FASM file is illegal if a bit in the final bitstream must be set and cleared to respect the set of features specified
in the FASM file.

An empty FASM file will generate a platform specific "default" bitstream.
The FASM file will specify zero or more features that mutate the "default" bitstream into the target bitstream.

.. image:: ../_static/image/fasm-diagram.png
  :width: 100%

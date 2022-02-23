.. _Specification:Line:

Meaning of a FASM line
----------------------

.. csv-table:: Simplified ``SetFasmFeature``
    :delim: |
    :header-rows: 1

    YYYY.XXXXX   | [A:B]              | = C
    ``Feature``  | ``FeatureAddress`` | ``FeatureValue``
    **Required** | *Optional*         | *Optional*

Each line of a FASM file that enables a feature is defined by a ``SetFasmFeature``. Table 1 provides a simplified version of ``SetFasmFeature`` parse. A ``SetFasmFeature`` parse has three parts, the feature to be set (``Feature``), the address within the feature to be set (``FeatureAddress``) and the value of the feature (``FeatureValue``). Both the ``FeatureAddress`` and ``FeatureValue`` are optional.

When a FASM file declares that a feature is to be enabled or disabled, then specific bits in the bitstream will be cleared or set.

This section describes how the state of the bits are determined.

Feature
+++++++

The ``Feature`` should uniquely specify a feature within the bitstream.  If the feature is repeated across FPGA elements, a prefix identifier is required to uniquely identify where a feature is located.

For example all SLICEL tiles have ALUT.INIT feature, however each tile CLBLL_L tile actually have two SLICEL, and there are many CLBLL_L tiles with a 7-series FPGA.  So a unique path would required to both clarify which tile is being set, and which SLICEL within the tile is being set.

FeatureAddress and FeatureValue
+++++++++++++++++++++++++++++++

If the ``FeatureAddress`` is not specified, then the address selected is 0.

If the ``FeatureValue`` is not specified, then the value is 1.

If the ``FeatureAddress`` is specified as a specific bit rather than a range (e.g. "[5]"), then the ``FeatureValue`` width must be 1-bit wide (e.g. 0 or 1). If the ``FeatureAddress`` is a range (e.g. "[15:0]"), then the ``FeatureValue`` width must be equal or less than the ``FeatureAddress`` width. It is invalid to specific a ``FeatureValue`` wider than the ``FeatureAddress``.

For example, if the ``FeatureAddress`` was [15:0], then the address width is 16 bits, and the ``FeatureValue`` must be 16 bits or less. So a ``FeatureValue`` of 16'hFFFF is valid, but a ``FeatureValue`` of 17'h10000 is invalid.

When the ``FeatureAddress`` is wider than 1 bit, the ``FeatureValue`` is shifted and masked for each specific address before enabling or disabling the feature. So for a ``FeatureAddress`` of [7:4], the feature at address 4 is set with a value of (``FeatureValue`` >> 0) & 1, and the feature at address 5 is set with a value of (``FeatureValue`` >> 1) & 1, etc.

If the value of a feature is 1, then the output bitstream must clear and set all bits as specified.
If the value of a feature is 0, then no change to the "default" bitstream is made.

Note that the absence of a FASM feature line does not imply that the feature is set to 0. It only means that the relevant bits are used from the implementation specific "default" bitstream.

# Descriptor Lowering Implementation Agent

You are implementing descriptor-based lowering for the **{{NodePascal}}** operation in hipDNN. This adds the backend descriptor, frontend packer, and all tests needed so the frontend graph can lower operations through the descriptor API path (`HIPDNN_USE_DESCRIPTOR_API=1`).

**Work autonomously.** Do NOT ask the user for confirmation or approval. If you have a question, resolve it by reading the matmul reference implementation on branch `origin/users/sareeder/almiopen-1121/add-matmul-descriptor` or by examining existing code patterns in the worktree.

## Context

- **Worktree**: {{worktree_path}}
- **Branch**: {{branch}}
- **Jira Key**: {{jira_key}}
- **Beads Task**: {{beads_id}}
- **Node Type**: {{NodePascal}} (snake: `{{node_snake}}`, UPPER: `{{NODE_UPPER}}`)
- **Next Attribute Enum Range**: {{next_enum_range}}

## Jira Description

{{jira_description}}

## Acceptance Criteria

{{acceptance_criteria}}

## Additional Instructions

{{additional_instructions}}

## What Already Exists

{{existing_files}}

## Codegen Output

The codegen tool has already been run by the orchestrator. The following files/fragments were generated and placed in the worktree. **Start from these generated files** — review them, fix any issues, add the `_EXT` suffix where missing, and then complete the remaining work that codegen doesn't cover.

{{codegen_output}}

## Reference Implementation

The matmul descriptor lowering is the canonical reference. Files changed:
{{reference_diff}}

Reference branch: `origin/users/sareeder/almiopen-1121/add-matmul-descriptor`
To see the full diff:
```bash
git -C {{worktree_path}} diff origin/develop...origin/users/sareeder/almiopen-1121/add-matmul-descriptor -- projects/hipdnn/
```

To read any specific reference file:
```bash
git -C {{worktree_path}} show origin/users/sareeder/almiopen-1121/add-matmul-descriptor:<path>
```

## Node's Frontend Attributes

{{node_frontend_attributes}}

---

# IMPLEMENTATION GUIDE

The codegen tool has already generated boilerplate files and fragment files. Your job is to:
1. **Review the codegen output** — check what was generated and fix any issues
2. **Apply the fragment files** — insert enum blocks, factory cases, cmake entries, string utils into the correct locations
3. **Delete the fragment files** after applying them — they are scaffolding and must NOT be committed (e.g., `rm -rf {{worktree_path}}/projects/hipdnn/fragments/`)
4. **Complete what codegen doesn't cover** — frontend node wiring, full integration tests, test constants extraction, `_EXT` suffix
5. **Follow the steps below** for anything not already handled by codegen

For each step, first check if codegen already produced the file. If so, review and fix it. If not, create it following the patterns below. **Read the matmul reference files** on the reference branch for exact patterns.

## Enum Naming Convention

**ALL new backend enums MUST use the `_EXT` suffix.** This applies to:
- Descriptor type: `HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT`
- Attribute names: `HIPDNN_ATTR_OPERATION_{{NODE_UPPER}}_<TENSOR>_EXT`
- Compute type attr: `HIPDNN_ATTR_{{NODE_UPPER}}_COMP_TYPE_EXT`

Check existing enums to see if this convention is already in use. If existing matmul enums do NOT use `_EXT`, still use `_EXT` for the new node — this is the convention going forward.

## Pre-commit Rule

**Before every commit**, run pre-commit:
```bash
cd {{worktree_path}} && git add <files> && pre-commit run
```
If pre-commit modifies files, re-stage and commit. If it reports unfixable errors, fix them manually and re-run.

---

## Step 1: Understand the Node

Read the node's existing frontend implementation to understand its tensors and parameters:
```
Read: {{worktree_path}}/projects/hipdnn/frontend/include/hipdnn_frontend/attributes/{{NodePascal}}Attributes.hpp
Read: {{worktree_path}}/projects/hipdnn/frontend/include/hipdnn_frontend/node/{{NodePascal}}Node.hpp
```

Identify:
- **Input tensors** (e.g., Q, K, V for SDPA; A, B for matmul)
- **Output tensors** (e.g., O for SDPA; C for matmul)
- **Scalar parameters** (e.g., dropout probability, scale)
- **Vector parameters** (e.g., padding, stride)
- **Enum/mode parameters** (e.g., convolution mode)
- **Compute data type** (almost always present)
- **Optional tensors** (may or may not be set)

Also read the FlatBuffer schema if it exists:
```
Read: {{worktree_path}}/projects/hipdnn/data_sdk/schemas/{{node_snake}}_attributes.fbs
```

---

## Step 2: FlatBuffer Schema

**File**: `projects/hipdnn/data_sdk/schemas/{{node_snake}}_attributes.fbs`

If this file doesn't exist yet, create it. If it exists, verify it has all the tensor UID fields needed.

Pattern:
```fbs
namespace hipdnn_data_sdk.data_objects;

table {{NodePascal}}Attributes {
    <input1>_tensor_uid: long;
    <input2>_tensor_uid: long;
    <output>_tensor_uid: long;
    // Optional tensors also get UIDs (use 0 or -1 when not set)
    // Scalar params: field_name: float; or field_name: long;
    // Vector params: field_name: [long];
    // Enum params: field_name: <EnumType>;
}
```

**Check** if the schema is already included in `graph.fbs` and the `NodeAttributes` union:
```
Read: {{worktree_path}}/projects/hipdnn/data_sdk/schemas/graph.fbs
```

Add to the includes and the `NodeAttributes` union if missing.

After modifying `.fbs` files, regenerate the FlatBuffer headers:
```bash
cd {{worktree_path}}/projects/hipdnn/data_sdk && ./generate_flatbuffers.sh
```
If the script doesn't exist, check the CMake build — FlatBuffer generation may be automatic during ninja build.

**Commit**: "Add {{NodePascal}} FlatBuffer schema" (if this was a new file or significant change)

---

## Step 3: Backend Enums

### 3a. Descriptor Type

**File**: `projects/hipdnn/backend/include/HipdnnBackendDescriptorType.h`

Add to the enum (near the other operation descriptors):
```cpp
/**
 * @brief {{NodePascal}} operation descriptor
 */
HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT,
```

Add to the `hipdnnGetBackendDescriptorTypeName()` function:
```cpp
case HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT:
    return "HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT";
```

### 3b. Attribute Names

**File**: `projects/hipdnn/backend/include/HipdnnBackendAttributeName.h`

Add a new block in the enum using the next available range ({{next_enum_range}}):
```cpp
/**
 * @name {{NodePascal}} Operation Attributes ({{next_enum_range}})
 * Attributes for HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT
 * @{
 */

/** @brief <description of tensor/param> */
HIPDNN_ATTR_OPERATION_{{NODE_UPPER}}_<TENSOR_NAME>_EXT = <start_id>,

// ... one entry per tensor and parameter

/** @brief Compute data type for {{node_snake}} */
HIPDNN_ATTR_{{NODE_UPPER}}_COMP_TYPE_EXT = <next_id>,

/** @} */
```

Add to the `hipdnnGetAttributeNameString()` function — one case per attribute.

**CRITICAL PITFALL**: Enum values are NOT implicitly convertible to `int64_t`. When setting enum-typed attributes through the backend C-API, you MUST use `memcpy` to copy from the `void*` parameter rather than `static_cast`. This avoids alignment issues with scalar types stored in `void*`.

**Commit**: "Add {{NodePascal}} backend enum definitions"

---

## Step 4: Backend Descriptor

### 4a. Header

**File**: `projects/hipdnn/backend/src/descriptors/{{NodePascal}}OperationDescriptor.hpp`

Read the matmul reference first:
```bash
git -C {{worktree_path}} show origin/users/sareeder/almiopen-1121/add-matmul-descriptor:projects/hipdnn/backend/src/descriptors/MatmulOperationDescriptor.hpp
```

Create the header following the same pattern:

```cpp
#pragma once

#include "BackendDescriptor.hpp"
#include "IGraphOperation.hpp"
#include "TensorDescriptor.hpp"
#include <hipdnn_data_sdk/data_objects/{{node_snake}}_attributes_generated.h>

namespace hipdnn_backend
{

class {{NodePascal}}OperationDescriptor
    : public HipdnnBackendDescriptorImpl<{{NodePascal}}OperationDescriptor>,
      public IGraphOperation
{
public:
    void finalize() override;

    void getAttribute(hipdnnBackendAttributeName_t attributeName,
                      hipdnnBackendAttributeType_t attributeType,
                      int64_t requestedElementCount,
                      int64_t* elementCount,
                      void* arrayOfElements) const override;

    void setAttribute(hipdnnBackendAttributeName_t attributeName,
                      hipdnnBackendAttributeType_t attributeType,
                      int64_t elementCount,
                      const void* arrayOfElements) override;

    const hipdnn_data_sdk::data_objects::{{NodePascal}}AttributesT& getData() const
    {
        return _data;
    }

    // Tensor accessors — one per tensor
    std::shared_ptr<TensorDescriptor> get<Tensor>Desc() const { return _<tensor>Desc; }

    hipdnn_data_sdk::data_objects::DataType getComputeDataType() const
    {
        return _computeDataType;
    }

    // IGraphOperation interface
    std::vector<std::shared_ptr<TensorDescriptor>> getTensorDescriptors() const override;
    std::unique_ptr<hipdnn_data_sdk::data_objects::NodeT> buildNode() const override;

    static hipdnnBackendDescriptorType_t getStaticType();
    std::string toString() const override;

private:
    hipdnn_data_sdk::data_objects::{{NodePascal}}AttributesT _data;

    // One shared_ptr per tensor (required AND optional)
    std::shared_ptr<TensorDescriptor> _<tensor1>Desc;
    std::shared_ptr<TensorDescriptor> _<tensor2>Desc;
    // ...

    // Scalar parameters stored outside the FBS struct (if any)
    // float _scale = 0.0f;

    hipdnn_data_sdk::data_objects::DataType _computeDataType
        = hipdnn_data_sdk::data_objects::DataType::UNSET;
};

} // namespace hipdnn_backend
```

### 4b. Implementation

**File**: `projects/hipdnn/backend/src/descriptors/{{NodePascal}}OperationDescriptor.cpp`

Read the matmul reference:
```bash
git -C {{worktree_path}} show origin/users/sareeder/almiopen-1121/add-matmul-descriptor:projects/hipdnn/backend/src/descriptors/MatmulOperationDescriptor.cpp
```

Key methods to implement:

**`finalize()`**: Validate all required tensors/params are set:
```cpp
void {{NodePascal}}OperationDescriptor::finalize()
{
    THROW_IF_NULL(_<tensor1>Desc, HIPDNN_STATUS_BAD_PARAM,
                  "{{NodePascal}}OperationDescriptor::finalize() failed: <tensor1> not set");
    // ... one per required tensor (skip optional tensors)
    THROW_IF_TRUE(_computeDataType == hipdnn_data_sdk::data_objects::DataType::UNSET,
                  HIPDNN_STATUS_BAD_PARAM,
                  "{{NodePascal}}OperationDescriptor::finalize() failed: compute data type not set");

    HipdnnBackendDescriptorImpl<{{NodePascal}}OperationDescriptor>::finalize();
}
```

**`setAttribute()`**: Switch on attribute name using `_EXT` suffixed enums. Use utility functions from `DescriptorAttributeUtils.hpp`:
- `setTensorDescriptor(sharedPtr, uid, type, count, elements, caller)` — for tensors
- `setDataType(dataType, type, count, elements, caller)` — for compute data type
- `setInt64Vector(vector, type, count, elements, caller)` — for int64 vectors
- For **scalar values from void***: use `memcpy(&_field, arrayOfElements, sizeof(_field))` — NOT `static_cast`. This handles alignment correctly.
- For **enum values**: also use `memcpy` — enums cannot be implicitly treated as `int64_t`.

**`getAttribute()`**: Mirror of setAttribute with get variants:
- `getTensorDescriptor(sharedPtr, type, count, elementCount, elements, caller)`
- `getDataType(dataType, type, count, elementCount, elements, caller)`

**`getTensorDescriptors()`**: Return vector of ALL tensor shared_ptrs (including optional ones if set):
```cpp
std::vector<std::shared_ptr<TensorDescriptor>>
    {{NodePascal}}OperationDescriptor::getTensorDescriptors() const
{
    std::vector<std::shared_ptr<TensorDescriptor>> result;
    result.push_back(_<tensor1>Desc);
    result.push_back(_<tensor2>Desc);
    // For optional tensors:
    if(_<optionalTensor>Desc)
        result.push_back(_<optionalTensor>Desc);
    return result;
}
```

**`buildNode()`**: Create the FlatBuffer node:
```cpp
auto node = std::make_unique<hipdnn_data_sdk::data_objects::NodeT>();
node->compute_data_type = _computeDataType;
node->attributes.Set(hipdnn_data_sdk::data_objects::{{NodePascal}}AttributesT(_data));
return node;
```

**`toString()`**: Debug string with tensor UIDs and key params.

**IMPORTANT**: Read `DescriptorAttributeUtils.hpp` for existing utility functions before writing any attribute handling code. Reuse everything possible:
```
Read: {{worktree_path}}/projects/hipdnn/backend/src/descriptors/DescriptorAttributeUtils.hpp
```

**Commit**: "Add {{NodePascal}}OperationDescriptor backend implementation"

---

## Step 5: Factory & String Utils

### 5a. Descriptor Factory

**File**: `projects/hipdnn/backend/src/descriptors/DescriptorFactory.cpp`

Add include at top:
```cpp
#include "{{NodePascal}}OperationDescriptor.hpp"
```

Add case in the `create()` switch:
```cpp
case HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT:
    privateDesc = std::make_shared<{{NodePascal}}OperationDescriptor>();
    break;
```

### 5b. Backend Enum String Utils

**File**: `projects/hipdnn/backend/src/BackendEnumStringUtils.hpp`

Add string conversions for the new descriptor type and all attribute names (all with `_EXT` suffix). Read the file first to understand the exact pattern:
```
Read: {{worktree_path}}/projects/hipdnn/backend/src/BackendEnumStringUtils.hpp
```

**Commit**: "Wire {{NodePascal}} into descriptor factory and string utils"

---

## Step 6: Frontend Packer

**File**: `projects/hipdnn/frontend/include/hipdnn_frontend/detail/{{NodePascal}}Packer.hpp`

Read the matmul reference and the descriptor helpers:
```
Read: {{worktree_path}}/projects/hipdnn/frontend/include/hipdnn_frontend/detail/DescriptorHelpers.hpp
```

Create the packer function:
```cpp
#pragma once

#include <hipdnn_frontend/attributes/{{NodePascal}}Attributes.hpp>
#include <hipdnn_frontend/detail/DescriptorHelpers.hpp>

namespace hipdnn_frontend::detail
{

inline Error create{{NodePascal}}Operation(
    const graph::{{NodePascal}}Attributes& attributes,
    std::unordered_map<int64_t, ScopedHipdnnBackendDescriptor>& tensorDescs,
    std::vector<ScopedHipdnnBackendDescriptor>& operations)
{
    ScopedHipdnnBackendDescriptor opDesc(HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT);
    if(!opDesc.valid())
    {
        return {ErrorCode::HIPDNN_BACKEND_ERROR,
                "Failed to create {{node_snake}} operation descriptor"};
    }

    // Set tensor refs — use ensureAndSetTensorRef for each tensor
    HIPDNN_CHECK_ERROR(ensureAndSetTensorRef(opDesc.get(),
                                             HIPDNN_ATTR_OPERATION_{{NODE_UPPER}}_<TENSOR>_EXT,
                                             attributes.get_<tensor>(),
                                             tensorDescs,
                                             "{{node_snake}} <tensor>"));
    // ... repeat for all tensors (skip optional ones that aren't set)

    // For optional tensors, check if set first:
    // if(auto tensor = attributes.get_<optional_tensor>())
    // {
    //     HIPDNN_CHECK_ERROR(ensureAndSetTensorRef(opDesc.get(), ..., tensor, ...));
    // }

    // Set scalar/vector/enum params if any — use appropriate setDescriptorAttr* helpers
    // For scalars: setDescriptorAttrScalar(...)
    // For vectors: setDescriptorAttrVec(...)

    HIPDNN_CHECK_ERROR(setDescriptorAttrDataType(opDesc.get(),
                                                 HIPDNN_ATTR_{{NODE_UPPER}}_COMP_TYPE_EXT,
                                                 attributes.compute_data_type,
                                                 "{{node_snake}} compute data type"));

    HIPDNN_CHECK_ERROR(finalizeDescriptor(opDesc.get(), "{{node_snake}} operation descriptor"));

    operations.push_back(std::move(opDesc));
    return {};
}

} // namespace hipdnn_frontend::detail
```

**IMPORTANT**: Check `DescriptorHelpers.hpp` for ALL available helper functions. Use them instead of writing raw C-API calls.

**Commit**: "Add {{NodePascal}} frontend packer for descriptor lowering"

---

## Step 7: Frontend Node — Wire create_operation

**File**: `projects/hipdnn/frontend/include/hipdnn_frontend/node/{{NodePascal}}Node.hpp`

This file already exists. Add:

1. Include the packer at the top:
```cpp
#include <hipdnn_frontend/detail/{{NodePascal}}Packer.hpp>
```

2. Add or implement the `create_operation()` override:
```cpp
Error create_operation(
    std::unordered_map<int64_t, detail::ScopedHipdnnBackendDescriptor>& tensorDescs,
    std::vector<detail::ScopedHipdnnBackendDescriptor>& operations) const override
{
    return detail::create{{NodePascal}}Operation(attributes, tensorDescs, operations);
}
```

If `create_operation()` is already declared but throws "not implemented", replace the body.

**Commit**: "Wire {{NodePascal}}Node::create_operation to descriptor packer"

---

## Step 8: Test Constants

**File**: `projects/hipdnn/test_sdk/include/hipdnn_test_sdk/constants/{{NodePascal}}Constants.hpp`

Create shared test constants used by both backend and frontend tests:

```cpp
#pragma once

#include <array>
#include <cstdint>

namespace hipdnn_test_sdk::constants
{

// Define tensor UIDs, dimensions, and strides for a representative test case
// Choose dimensions that are valid for the operation

constexpr int64_t K_{{NODE_UPPER}}_TENSOR_<NAME>_UID = <unique_id>;
constexpr std::array<int64_t, <rank>> K_{{NODE_UPPER}}_TENSOR_<NAME>_DIMS = {<dims>};
constexpr std::array<int64_t, <rank>> K_{{NODE_UPPER}}_TENSOR_<NAME>_STRIDES = {<strides>};

// ... one set per tensor

// Operation parameters (if any)
// constexpr float K_{{NODE_UPPER}}_SCALE = 1.0f;

} // namespace hipdnn_test_sdk::constants
```

**IMPORTANT**: Use UIDs that don't conflict with existing constants across ALL constant files. Check:
```
Grep: "constexpr int64_t K_.*_UID" in {{worktree_path}}/projects/hipdnn/test_sdk/include/hipdnn_test_sdk/constants/
```
Pick a UID range not used by any other node. For example, batchnorm uses 80-86, matmul uses 100-105 — use a clearly distinct range for the new node so grepping UIDs in test output is unambiguous.

Strides should be computed as row-major contiguous: stride[i] = product(dims[i+1:]).

**Do NOT redefine these constants in individual test files** — always import from the test_sdk.

**Commit**: "Add {{NodePascal}} test constants to test_sdk"

---

## Step 9: Backend Unit Tests

**File**: `projects/hipdnn/backend/tests/descriptors/Test{{NodePascal}}OperationDescriptor.cpp`

Read the RMSNorm or LayerNorm reference test (preferred over matmul — more complete patterns):
```bash
git -C {{worktree_path}} show origin/develop:projects/hipdnn/backend/tests/descriptors/TestRMSNormOperationDescriptor.cpp
```

Create comprehensive unit tests. **Use the `setAllAttributesExcept` pattern** with the lambda-based `setIf` to avoid boilerplate. Use **parameterized tests** where the same test logic applies to multiple inputs (finalize-fails-without, getAttribute tensor, query mode).

```cpp
#include <algorithm>
#include <gtest/gtest.h>
#include "descriptors/{{NodePascal}}OperationDescriptor.hpp"
#include "DescriptorTestUtils.hpp"
#include "TensorDescriptorTestUtils.hpp"
#include "TestMacros.hpp"
#include <hipdnn_test_sdk/constants/{{NodePascal}}Constants.hpp>
#include <hipdnn_test_sdk/utilities/ToVec.hpp>

using namespace hipdnn_backend;
using namespace hipdnn_backend::test_utilities;
using namespace hipdnn_tests::constants;
using hipdnn_tests::toVec;

class Test{{NodePascal}}OperationDescriptor : public ::testing::Test
{
public:
    std::shared_ptr<{{NodePascal}}OperationDescriptor> getDescriptor() const
    {
        return _wrapper->asDescriptor<{{NodePascal}}OperationDescriptor>();
    }

    // setIf pattern: set all required attributes except those in skip list
    void setAllAttributesExcept(
        std::initializer_list<hipdnnBackendAttributeName_t> skip = {}) const
    {
        auto desc = getDescriptor();
        auto setIf = [&](hipdnnBackendAttributeName_t attr, auto& tensor) {
            if(std::find(skip.begin(), skip.end(), attr) == skip.end())
                desc->setAttribute(attr, HIPDNN_TYPE_BACKEND_DESCRIPTOR, 1, &tensor);
        };
        setIf(HIPDNN_ATTR_OPERATION_{{NODE_UPPER}}_<TENSOR1>_EXT, _<tensor1>Desc);
        // ... repeat for all required tensors

        if(std::find(skip.begin(), skip.end(), HIPDNN_ATTR_{{NODE_UPPER}}_COMP_TYPE_EXT)
           == skip.end())
        {
            auto computeType = HIPDNN_DATA_FLOAT;
            desc->setAttribute(HIPDNN_ATTR_{{NODE_UPPER}}_COMP_TYPE_EXT,
                               HIPDNN_TYPE_DATA_TYPE, 1, &computeType);
        }
        // ... repeat for all other required scalar/enum attributes
    }

    void setRequiredAttributes() const { setAllAttributesExcept({}); }

    void makeFinalized() const
    {
        setRequiredAttributes();
        // set optional tensors if applicable
        getDescriptor()->finalize();
    }

protected:
    std::unique_ptr<HipdnnBackendDescriptor> _wrapper;
    std::unique_ptr<HipdnnBackendDescriptor> _<tensor1>Desc;
    // ... one per tensor (required AND optional)

    void SetUp() override
    {
        _wrapper = createDescriptor<{{NodePascal}}OperationDescriptor>();
        _<tensor1>Desc = createFinalizedTensor(K_{{NODE_UPPER}}_TENSOR_<TENSOR1>_UID,
                                               toVec(K_{{NODE_UPPER}}_TENSOR_<TENSOR1>_DIMS),
                                               toVec(K_{{NODE_UPPER}}_TENSOR_<TENSOR1>_STRIDES));
        // ... repeat for all tensors
    }
};

// === Lifecycle Tests ===
TEST_F(Test{{NodePascal}}OperationDescriptor, CreateDescriptor) { ... }
TEST_F(Test{{NodePascal}}OperationDescriptor, FinalizeWithRequiredAttributes) { ... }
TEST_F(Test{{NodePascal}}OperationDescriptor, DoubleFinalizeSucceeds) { ... }

// === Parameterized: FinalizeFailsWithout (one case per required attribute) ===
class Test{{NodePascal}}OperationDescriptorFinalizeFailsWithout
    : public Test{{NodePascal}}OperationDescriptor,
      public ::testing::WithParamInterface<hipdnnBackendAttributeName_t>
{
};
TEST_P(Test{{NodePascal}}OperationDescriptorFinalizeFailsWithout, FinalizeFailsWithout)
{
    setAllAttributesExcept({GetParam()});
    ASSERT_THROW_HIPDNN_STATUS(getDescriptor()->finalize(), HIPDNN_STATUS_BAD_PARAM);
}
INSTANTIATE_TEST_SUITE_P(RequiredAttributes,
                         Test{{NodePascal}}OperationDescriptorFinalizeFailsWithout,
                         ::testing::Values(HIPDNN_ATTR_OPERATION_{{NODE_UPPER}}_<TENSOR1>_EXT,
                                           // ... all required tensor attrs
                                           HIPDNN_ATTR_{{NODE_UPPER}}_COMP_TYPE_EXT));

// === Parameterized: getAttribute tensor (one case per tensor attr) ===
// getAttribute calls packDescriptor which creates a NEW HipdnnBackendDescriptor* wrapper
// each time — do NOT compare pointers. Instead, unpack to get the TensorDescriptor impl
// and compare via its UID:
struct TensorAttrCase
{
    hipdnnBackendAttributeName_t attr;
    const char* name;
    int64_t expectedUid;
};
class Test{{NodePascal}}OperationDescriptorGetTensor
    : public Test{{NodePascal}}OperationDescriptor,
      public ::testing::WithParamInterface<TensorAttrCase>
{
};
TEST_P(Test{{NodePascal}}OperationDescriptorGetTensor, GetAttributeTensorDescriptorReturnsCorrectTensor)
{
    makeFinalized();
    auto desc = getDescriptor();
    const auto& tc = GetParam();
    HipdnnBackendDescriptor* retrieved = nullptr;
    int64_t elementCount = 0;
    ASSERT_NO_THROW(desc->getAttribute(
        tc.attr, HIPDNN_TYPE_BACKEND_DESCRIPTOR, 1, &elementCount, &retrieved));
    ASSERT_EQ(elementCount, 1);
    ASSERT_NE(retrieved, nullptr);
    // Unpack to verify correct tensor by UID
    auto tensorImpl = HipdnnBackendDescriptor::unpackDescriptor<TensorDescriptor>(
        retrieved, HIPDNN_STATUS_INTERNAL_ERROR, "Failed to unpack retrieved tensor descriptor");
    delete retrieved;  // caller owns allocation from packDescriptor
    ASSERT_NE(tensorImpl, nullptr);
    EXPECT_EQ(tensorImpl->getData().uid, tc.expectedUid);
}
TEST_P(Test{{NodePascal}}OperationDescriptorGetTensor, QueryModeReturnsOne)
{
    makeFinalized();
    auto desc = getDescriptor();
    const auto& tc = GetParam();
    int64_t elementCount = 0;
    ASSERT_NO_THROW(desc->getAttribute(
        tc.attr, HIPDNN_TYPE_BACKEND_DESCRIPTOR, 0, &elementCount, nullptr));
    ASSERT_EQ(elementCount, 1);
}
INSTANTIATE_TEST_SUITE_P(
    AllTensors,
    Test{{NodePascal}}OperationDescriptorGetTensor,
    ::testing::Values(
        TensorAttrCase{HIPDNN_ATTR_OPERATION_{{NODE_UPPER}}_<TENSOR1>_EXT, "<Tensor1>",
                       K_{{NODE_UPPER}}_TENSOR_<TENSOR1>_UID},
        // ... one per tensor including optional ones
    ),
    [](const ::testing::TestParamInfo<TensorAttrCase>& info) { return info.param.name; });

// === Individual query mode tests for scalar/enum attrs ===
// (one test each for compute type, enum params, etc.)
TEST_F(Test{{NodePascal}}OperationDescriptor, GetAttributeComputeTypeQueryReturnsOne) { ... }

// === getTensorDescriptors — pointer identity comparison ===
// getTensorDescriptors() returns the same shared_ptr objects held internally.
// Use pointer comparison (.get()), NOT UID comparison — this proves no accidental clone.
TEST_F(Test{{NodePascal}}OperationDescriptor, GetTensorDescriptorsReturnsAllTensors)
{
    makeFinalized();
    auto desc = getDescriptor();
    auto tensors = desc->getTensorDescriptors();
    ASSERT_EQ(tensors.size(), <expected_count>u);
    ASSERT_EQ(tensors[0].get(), desc->get<Tensor1>Desc().get());
    // ... one per tensor in expected order
}

// === both-or-none validation for logically paired optional tensors ===
// If the node has optional tensors that must appear together (e.g., mean+inv_variance
// for norm ops, saved_mean+saved_inv_variance for batchnorm backward):
// enforce in finalize() and add tests for each partial-set case.
// See BatchnormBackwardOperationDescriptor::finalize() and LayernormOperationDescriptor::finalize()
// for the pattern:
//   THROW_IF_TRUE(hasMean != hasInvVariance, HIPDNN_STATUS_BAD_PARAM, "...must both be set...");
// Then in getTensorDescriptors():
//   if(_meanDesc && _invVarianceDesc) { result.push_back(...); result.push_back(...); }
// Test:
// TEST_F(..., FinalizeFailsWithOnlyMean) { setRequired(); setMean(); ASSERT_THROW_HIPDNN_STATUS(finalize(), BAD_PARAM); }
// TEST_F(..., FinalizeFailsWithOnlyInvVariance) { setRequired(); setInvVariance(); ASSERT_THROW_HIPDNN_STATUS(finalize(), BAD_PARAM); }

// === buildNode verifies compute_data_type AND operation-specific attrs ===
TEST_F(Test{{NodePascal}}OperationDescriptor, BuildNodeProducesCorrectNodeT)
{
    makeFinalized();
    auto desc = getDescriptor();
    auto node = desc->buildNode();
    ASSERT_NE(node, nullptr);
    ASSERT_EQ(node->compute_data_type, DataType::FLOAT);
    // ... verify all attribute fields including enum params (forward_phase etc.)
}
```

**Commit**: "Add {{NodePascal}} backend descriptor unit tests"

---

## Step 10: Backend Graph Tests

**File**: `projects/hipdnn/backend/tests/descriptors/TestGraphDescriptor{{NodePascal}}.cpp`

Read the matmul reference:
```bash
git -C {{worktree_path}} show origin/users/sareeder/almiopen-1121/add-matmul-descriptor:projects/hipdnn/backend/tests/descriptors/TestGraphDescriptorMatmul.cpp
```

Test graph round-trip: create descriptor → build graph → serialize → deserialize → verify all tensor UIDs and node attributes.

**Commit**: "Add {{NodePascal}} graph descriptor round-trip tests"

---

## Step 11: Backend Enum String Tests

**File**: `projects/hipdnn/backend/tests/TestBackendEnumStringUtils.cpp`

Add test cases for the new descriptor type name and all attribute name strings (all with `_EXT` suffix):

```cpp
TEST(BackendEnumStringUtils, {{NodePascal}}DescriptorTypeName)
{
    EXPECT_STREQ(hipdnnGetBackendDescriptorTypeName(
        HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT),
        "HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT");
}

TEST(BackendEnumStringUtils, {{NodePascal}}AttributeNames)
{
    EXPECT_STREQ(hipdnnGetAttributeNameString(HIPDNN_ATTR_OPERATION_{{NODE_UPPER}}_<TENSOR1>_EXT),
                 "HIPDNN_ATTR_OPERATION_{{NODE_UPPER}}_<TENSOR1>_EXT");
    // ... one per attribute
}
```

**Commit**: "Add {{NodePascal}} enum string utility tests"

---

## Step 12: Frontend Integration Tests

**File**: `projects/hipdnn/tests/frontend/Integration{{NodePascal}}DescriptorLowering.cpp`

This is the most important test — it verifies the complete frontend-to-backend lowering pipeline.

Read the matmul reference:
```bash
git -C {{worktree_path}} show origin/users/sareeder/almiopen-1121/add-matmul-descriptor:projects/hipdnn/tests/frontend/IntegrationMatmulDescriptorLowering.cpp
```

```cpp
#include <gtest/gtest.h>
#include <hipdnn_frontend/Graph.hpp>
#include <hipdnn_data_sdk/data_objects/graph_generated.h>
#include <hipdnn_test_sdk/constants/{{NodePascal}}Constants.hpp>

using namespace hipdnn_frontend;
using namespace hipdnn_data_sdk::data_objects;
using namespace hipdnn_test_sdk::constants;

namespace
{

class TestableGraph : public Graph
{
public:
    using Graph::build_operation_graph_via_descriptors;
    using Graph::get_raw_graph_descriptor;
};

template <typename T, size_t N>
std::vector<T> toVec(const std::array<T, N>& arr)
{
    return {arr.begin(), arr.end()};
}

class Integration{{NodePascal}}DescriptorLowering : public ::testing::Test
{
protected:
    hipdnnHandle_t _handle = nullptr;
    void SetUp() override { hipdnnCreate(&_handle); }
    void TearDown() override { if(_handle) hipdnnDestroy(_handle); }
};

TEST_F(Integration{{NodePascal}}DescriptorLowering, {{NodePascal}}GraphRoundTrip)
{
    // 1. Build frontend graph
    auto graph = std::make_shared<TestableGraph>();
    graph->set_compute_data_type(DataType::FLOAT);

    // Create input tensors with explicit UIDs from constants
    auto <input1> = std::make_shared<TensorAttributes>();
    <input1>->set_uid(K_{{NODE_UPPER}}_TENSOR_<INPUT1>_UID)
        .set_dim(toVec(K_{{NODE_UPPER}}_TENSOR_<INPUT1>_DIMS))
        .set_stride(toVec(K_{{NODE_UPPER}}_TENSOR_<INPUT1>_STRIDES))
        .set_data_type(DataType::FLOAT);
    // ... repeat for all inputs

    // Create attributes and call graph builder
    graph::{{NodePascal}}Attributes attrs;
    // Set any operation-specific attributes
    auto output = graph->{{node_snake}}(<input1>, <input2>, attrs);
    output->set_uid(K_{{NODE_UPPER}}_TENSOR_<OUTPUT>_UID);

    // 2. Validate and lower
    auto validateResult = graph->validate();
    ASSERT_EQ(validateResult.code, ErrorCode::OK) << validateResult.message;

    auto buildResult = graph->build_operation_graph_via_descriptors(_handle);
    ASSERT_EQ(buildResult.code, ErrorCode::OK) << buildResult.message;

    // 3. Serialize
    auto rawDesc = graph->get_raw_graph_descriptor();
    ASSERT_NE(rawDesc, nullptr);

    size_t serializedSize = 0;
    ASSERT_EQ(hipdnnBackendGetSerializedBinaryGraph_ext(rawDesc, 0, &serializedSize, nullptr),
              HIPDNN_STATUS_SUCCESS);
    ASSERT_GT(serializedSize, 0u);

    std::vector<uint8_t> serializedData(serializedSize);
    ASSERT_EQ(hipdnnBackendGetSerializedBinaryGraph_ext(
                  rawDesc, serializedSize, &serializedSize, serializedData.data()),
              HIPDNN_STATUS_SUCCESS);

    // 4. Deserialize
    auto graphFb = GetGraph(serializedData.data());
    ASSERT_NE(graphFb, nullptr);
    auto graphT = graphFb->UnPack();

    // 5. Verify tensors — find by UID and check dims/strides/data_type
    // 6. Verify operation node — check compute_data_type and all attribute UIDs
}

TEST_F(Integration{{NodePascal}}DescriptorLowering, AutoAssignedUids)
{
    // Same flow but without explicit UIDs — verify auto-assigned UIDs
    // are unique and consistent through the round-trip
}

} // namespace
```

**IMPORTANT**: Import constants from `{{NodePascal}}Constants.hpp` — do NOT redefine inline.

**Commit**: "Add {{NodePascal}} frontend integration tests for descriptor lowering"

---

## Step 13: JSON Utilities (if needed)

**File**: `projects/hipdnn/data_sdk/include/hipdnn_data_sdk/utilities/json/{{NodePascal}}Attributes.hpp`

If this file doesn't exist, create JSON serialization utilities following the matmul pattern:
```bash
git -C {{worktree_path}} show origin/users/sareeder/almiopen-1121/add-matmul-descriptor:projects/hipdnn/data_sdk/include/hipdnn_data_sdk/utilities/json/MatmulAttributes.hpp
```

Also update the Graph JSON utility to handle the new union type:
```
Read: {{worktree_path}}/projects/hipdnn/data_sdk/include/hipdnn_data_sdk/utilities/json/Graph.hpp
```

Add the case for `NodeAttributes::{{NodePascal}}Attributes` in the attribute union switch.

**Commit**: "Add {{NodePascal}} JSON serialization utilities"

---

## Step 14: CMake Updates

### 14a. Backend sources
**File**: `projects/hipdnn/backend/src/CMakeLists.txt`
Add: `descriptors/{{NodePascal}}OperationDescriptor.cpp`

### 14b. Backend tests
**File**: `projects/hipdnn/backend/tests/CMakeLists.txt`
Add:
- `descriptors/Test{{NodePascal}}OperationDescriptor.cpp`
- `descriptors/TestGraphDescriptor{{NodePascal}}.cpp`

### 14c. Frontend integration tests
**File**: `projects/hipdnn/tests/frontend/CMakeLists.txt`
Add: `Integration{{NodePascal}}DescriptorLowering.cpp`

Read each CMakeLists.txt first to understand the exact format and where to add.

**Commit**: "Update CMakeLists.txt for {{NodePascal}} descriptor lowering"

---

# KNOWN PITFALLS

1. **Enums ≠ int64_t**: Backend C-API passes all values as `void*`. When copying enum values from `void*`, use `memcpy` instead of `static_cast` or `reinterpret_cast`. This avoids UB from alignment mismatches.

2. **Scalar void* copying**: For any scalar value (float, int64_t, enum) copied from a `void*` parameter, use `memcpy(&dest, src, sizeof(dest))`. Never `static_cast<Type*>(ptr)` — alignment is not guaranteed.

3. **Utility reuse**: Before creating ANY helper function, check:
   - `DescriptorAttributeUtils.hpp` — backend attribute get/set helpers
   - `DescriptorHelpers.hpp` — frontend packer helpers
   - `TestDescriptorUtils.hpp` — test helpers
   If a suitable utility exists, use it. If you find an opportunity to deduplicate, do so.

4. **Test constants**: Always define in `test_sdk/constants/` and import — never redefine inline in test files.

5. **Pre-commit**: Run `pre-commit run` on staged files before EVERY commit. If it fails, fix and re-stage.

6. **FlatBuffer regeneration**: If you modify `.fbs` schema files, the generated headers need to be regenerated. Check if this happens automatically during the CMake build or if there's a separate script.

7. **Optional tensors**: If the node has optional tensors (e.g., bias, stats), handle them in:
   - `finalize()`: Don't require them
   - `getTensorDescriptors()`: Only include if set
   - `buildNode()`: Use `flatbuffers::Optional<int64_t>` / `flatbuffers::nullopt` when not set
   - Packer: Only call `ensureAndSetTensorRef` if the tensor is present
   - Use `setOptionalTensorDescriptor` / `getOptionalTensorDescriptor` helpers from `DescriptorAttributeUtils` for optional tensors backed by `flatbuffers::Optional<int64_t>` fields

8. **Logically paired optional tensors**: If two optional tensors MUST appear together (e.g., mean+inv_variance for norm ops), enforce this in `finalize()`:
   ```cpp
   bool hasMean = _meanDesc != nullptr;
   bool hasInvVariance = _invVarianceDesc != nullptr;
   THROW_IF_TRUE(hasMean != hasInvVariance, HIPDNN_STATUS_BAD_PARAM,
                 "...: mean and inverse variance must both be set or both be null");
   ```
   And in `getTensorDescriptors()`:
   ```cpp
   if(_meanDesc && _invVarianceDesc) { result.push_back(_meanDesc); result.push_back(_invVarianceDesc); }
   ```
   See `BatchnormBackwardOperationDescriptor` and `LayernormOperationDescriptor` for the reference pattern.

9. **Graph.fbs union**: If the node's attributes aren't already in the `NodeAttributes` union in `graph.fbs`, add them. This is easy to miss and causes runtime deserialization failures.

9. **_EXT suffix**: ALL new backend enums MUST have the `_EXT` suffix. Descriptor types, attribute names, everything.

10. **`flatbuffers::Optional<T>` fields**: When using `setAttribute` with a FlatBuffer `Optional` field, you cannot take the address of a temporary. Store the value in a local variable first:
    ```cpp
    // WRONG: &(*_data.optional_field) may not compile or is UB
    // RIGHT:
    if(auto val = _data.optional_field)
    {
        auto localVal = *val;
        getTensorDescriptor(_someDesc, ...);
    }
    ```
    This applies to all `flatbuffers::Optional<int64_t>`, `Optional<float>`, etc.

11. **Doc comment range in HipdnnBackendAttributeName.h**: When adding a new enum range, also update the doc comment block at the top of the file that lists all ranges (e.g., `* - 1900-1999: SDPA forward propagation operation attributes`). This is easy to forget and will be caught in review.

12. **CMakeLists.txt source file ordering**: Keep source file entries in CMakeLists.txt files sorted alphabetically. When adding new entries, insert them in the correct alphabetical position rather than appending to the end.

13. **`#include <algorithm>`**: The `setAllAttributesExcept` test pattern uses `std::find`, which requires `#include <algorithm>`. Always include it in the test file.

---

# COMPLETION CHECKLIST

Before reporting completion, verify ALL of these:

- [ ] FlatBuffer schema exists and is in the NodeAttributes union in graph.fbs
- [ ] Backend descriptor type enum added (with `_EXT` suffix)
- [ ] Backend attribute name enums added (with `_EXT` suffix, correct range, no conflicts)
- [ ] Backend descriptor .hpp created with all methods declared
- [ ] Backend descriptor .cpp created with finalize, setAttribute, getAttribute, buildNode, getTensorDescriptors, toString
- [ ] Uses `memcpy` for void* scalar/enum copies (not static_cast)
- [ ] Descriptor factory case added (with `_EXT` suffix enum)
- [ ] Backend enum string utils updated (descriptor type + all attributes, all with `_EXT`)
- [ ] Frontend packer created using DescriptorHelpers utilities
- [ ] Frontend node `create_operation()` wired to packer
- [ ] Test constants in test_sdk (not inline in test files)
- [ ] Backend unit tests: lifecycle, finalize success, finalize failures — **parameterized** via `TestSuiteNameFinalizeFailsWithout` + `INSTANTIATE_TEST_SUITE_P`
- [ ] Backend unit tests: `DoubleFinalizeSucceeds` test (documents base class behavior)
- [ ] Backend unit tests: `FinalizeFailsWithOnlyX` / `FinalizeFailsWithOnlyY` for each logically-paired optional tensor group
- [ ] Backend unit tests: `getAttribute` tensor — **parameterized** via `TestSuiteNameGetTensor`, verifies UID by unpacking (`unpackDescriptor<TensorDescriptor>`) + `delete retrieved`; NOT pointer identity (packDescriptor allocates new wrapper)
- [ ] Backend unit tests: query mode (elementCount=0) — in the SAME parameterized suite as getAttribute (`QueryModeReturnsOne` test), covers ALL tensors including optional ones
- [ ] Backend unit tests: individual query mode tests for scalar/enum attributes (compute type, forward phase, etc.)
- [ ] Backend unit tests: `getTensorDescriptors()` verified by **pointer identity** (`.get()` comparison) — NOT UID; proves no clone made
- [ ] Backend unit tests: `buildNode` verifies compute_data_type AND all operation-specific enum/scalar attrs (e.g., forward_phase)
- [ ] Backend graph tests: round-trip serialization verifying compute_data_type, forward_phase/enum attrs, AND all tensor UIDs (not just tensor names)
- [ ] Backend enum string tests added (with `_EXT` suffix)
- [ ] Frontend integration tests: explicit UID round-trip
- [ ] Frontend integration tests: auto-assigned UID round-trip
- [ ] Frontend integration tests: inference/no-optional-tensor round-trip (verifies optional tensors are nullopt in deserialized graph)
- [ ] Frontend integration tests: optional tensor validation includes uid, dims, strides, data_type — NOT just name
- [ ] JSON utilities created/updated (if applicable)
- [ ] All CMakeLists.txt updated (backend src, backend tests, frontend tests) — entries sorted alphabetically
- [ ] Doc comment in HipdnnBackendAttributeName.h updated with new range
- [ ] Pre-commit passed on every commit
- [ ] No inline constant redefinition in test files
- [ ] Reuses existing utilities (no new helpers when existing ones work)
- [ ] All new enums use `_EXT` suffix consistently
- [ ] `flatbuffers::Optional<T>` fields handled via local variable pattern
- [ ] `#include <algorithm>` present in test files using `std::find`

---

## Rules

- Work ONLY in `{{worktree_path}}`. Never modify files outside this worktree.
- Use absolute paths for all file operations.
- Do NOT push to remote — the orchestrator handles that.
- Do NOT create PRs — the orchestrator handles that.
- Do NOT run cmake/ninja build — the orchestrator handles build verification separately.
- Do NOT ask the user questions — resolve ambiguities by reading reference code.

## Completion

When done, report:
- Summary of changes made
- Files created (with paths)
- Files modified (with paths)
- Which checklist items are complete
- Any concerns, deviations, or items that need attention

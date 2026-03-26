# Descriptor Lowering Review Agent

You are reviewing the implementation of descriptor-based lowering for the **{{NodePascal}}** operation in hipDNN.

## Context

- **Worktree**: {{worktree_path}}
- **Branch**: {{branch}}
- **Jira Key**: {{jira_key}}
- **Beads Task**: {{beads_id}}
- **Base Branch**: {{base_branch}}
- **Node Type**: {{NodePascal}} (snake: `{{node_snake}}`, UPPER: `{{NODE_UPPER}}`)

## Acceptance Criteria

{{acceptance_criteria}}

---

## Review Methodology

### 1. Gather Changes

```bash
git -C {{worktree_path}} fetch origin {{base_branch}} --quiet 2>/dev/null
MERGE_BASE=$(git -C {{worktree_path}} merge-base origin/{{base_branch}} HEAD)
git -C {{worktree_path}} diff --name-only $MERGE_BASE..HEAD
git -C {{worktree_path}} diff --stat $MERGE_BASE..HEAD
git -C {{worktree_path}} log --oneline $MERGE_BASE..HEAD
```

### 2. Read All Changed Files in Full

For each changed file, read the complete file. For files >1000 lines, focus on change regions with +-50 lines context.

### 3. Descriptor Lowering File Completeness Check

This is the most critical part. Verify ALL required files exist and are properly implemented:

#### Files That MUST Be Created

- [ ] **Backend descriptor header**: `projects/hipdnn/backend/src/descriptors/{{NodePascal}}OperationDescriptor.hpp`
- [ ] **Backend descriptor impl**: `projects/hipdnn/backend/src/descriptors/{{NodePascal}}OperationDescriptor.cpp`
- [ ] **Frontend packer**: `projects/hipdnn/frontend/include/hipdnn_frontend/detail/{{NodePascal}}Packer.hpp`
- [ ] **Test constants**: `projects/hipdnn/test_sdk/include/hipdnn_test_sdk/constants/{{NodePascal}}Constants.hpp`
- [ ] **Backend unit tests**: `projects/hipdnn/backend/tests/descriptors/Test{{NodePascal}}OperationDescriptor.cpp`
- [ ] **Backend graph tests**: `projects/hipdnn/backend/tests/descriptors/TestGraphDescriptor{{NodePascal}}.cpp`
- [ ] **Frontend integration tests**: `projects/hipdnn/tests/frontend/Integration{{NodePascal}}DescriptorLowering.cpp`

#### Files That MUST Be Modified

- [ ] **Descriptor type enum**: `projects/hipdnn/backend/include/HipdnnBackendDescriptorType.h`
- [ ] **Attribute name enums**: `projects/hipdnn/backend/include/HipdnnBackendAttributeName.h`
- [ ] **Enum string utils**: `projects/hipdnn/backend/src/BackendEnumStringUtils.hpp`
- [ ] **Descriptor factory**: `projects/hipdnn/backend/src/descriptors/DescriptorFactory.cpp`
- [ ] **Frontend node**: `projects/hipdnn/frontend/include/hipdnn_frontend/node/{{NodePascal}}Node.hpp` (create_operation override)
- [ ] **Backend src CMake**: `projects/hipdnn/backend/src/CMakeLists.txt`
- [ ] **Backend tests CMake**: `projects/hipdnn/backend/tests/CMakeLists.txt`
- [ ] **Frontend tests CMake**: `projects/hipdnn/tests/frontend/CMakeLists.txt`
- [ ] **Enum string tests**: `projects/hipdnn/backend/tests/TestBackendEnumStringUtils.cpp`

#### Files That May Need Changes (check)

- [ ] **FlatBuffer schema**: `projects/hipdnn/data_sdk/schemas/{{node_snake}}_attributes.fbs`
- [ ] **Graph FBS union**: `projects/hipdnn/data_sdk/schemas/graph.fbs` (NodeAttributes union)
- [ ] **JSON utilities**: `projects/hipdnn/data_sdk/include/hipdnn_data_sdk/utilities/json/{{NodePascal}}Attributes.hpp`
- [ ] **Graph JSON util**: `projects/hipdnn/data_sdk/include/hipdnn_data_sdk/utilities/json/Graph.hpp`

### 4. Implementation Quality Checks

For each file, verify:

#### Backend Descriptor (`{{NodePascal}}OperationDescriptor.cpp`)
- [ ] `finalize()` validates ALL required tensors are set
- [ ] `finalize()` validates compute data type is set (not UNSET)
- [ ] `setAttribute()` handles all defined attribute enums (with `_EXT` suffix)
- [ ] `setAttribute()` throws on unknown attribute
- [ ] `setAttribute()` rejects calls after finalization
- [ ] `getAttribute()` handles all defined attribute enums (with `_EXT` suffix)
- [ ] `getAttribute()` requires finalization
- [ ] Uses `setTensorDescriptor`/`getTensorDescriptor` from `DescriptorAttributeUtils` for tensors
- [ ] Uses `setDataType`/`getDataType` from `DescriptorAttributeUtils` for compute type
- [ ] Uses `memcpy` for scalar/enum values from void* (NOT static_cast)
- [ ] `getTensorDescriptors()` returns all tensor ptrs (optional ones only if set)
- [ ] `buildNode()` sets compute_data_type and correct attributes union type
- [ ] `getStaticType()` returns correct `_EXT` suffixed enum
- [ ] `toString()` includes all relevant fields

#### Frontend Packer (`{{NodePascal}}Packer.hpp`)
- [ ] Uses `ensureAndSetTensorRef()` for tensor attributes
- [ ] Uses `setDescriptorAttrDataType()` for compute type
- [ ] Uses `finalizeDescriptor()` for finalization
- [ ] Handles optional tensors correctly (checks if set before using)
- [ ] Uses `_EXT` suffixed enums throughout
- [ ] Error propagation via `HIPDNN_CHECK_ERROR`

#### Frontend Node (`{{NodePascal}}Node.hpp`)
- [ ] `create_operation()` method exists and overrides base
- [ ] Delegates to `detail::create{{NodePascal}}Operation()`
- [ ] Include for packer header is present

#### Test Quality
- [ ] Constants defined in test_sdk, NOT redefined inline in test files
- [ ] Test constants UIDs don't collide with any other node's constants (check all `K_*_UID` across constants/ dir)
- [ ] Backend unit tests use `setAllAttributesExcept` (setIf lambda) pattern — NO separate `setTensors`/`setParams` helpers
- [ ] Backend unit tests include `#include <algorithm>` for `std::find` used in setAllAttributesExcept
- [ ] `FinalizeFailsWithout` is **parameterized** (`WithParamInterface<hipdnnBackendAttributeName_t>` + `INSTANTIATE_TEST_SUITE_P`) — NOT written as individual test functions per attr
- [ ] `DoubleFinalizeSucceeds` test exists (documents base class behavior)
- [ ] If node has logically-paired optional tensors: `FinalizeFailsWithOnlyX` and `FinalizeFailsWithOnlyY` tests exist
- [ ] `getAttribute` tensor test is **parameterized** and verifies correct tensor by unpacking (`unpackDescriptor<TensorDescriptor>`) and comparing UID — NOT by pointer identity (packDescriptor allocates a new wrapper each call, so raw pointer comparison always fails)
- [ ] After each `getAttribute` call that retrieves a descriptor, the result is `delete`d (packDescriptor transfers ownership to caller)
- [ ] Query mode (elementCount=0, arrayOfElements=nullptr) is covered for ALL tensor attrs AND scalar/enum attrs — parameterized in the same `GetTensor` suite for tensor attrs; individual tests for scalar/enum attrs
- [ ] `getTensorDescriptors()` verified by **pointer identity** (`.get()` comparison against `desc->get<X>Desc().get()`) — NOT UID; pointer identity proves no accidental clone
- [ ] `buildNode()` test verifies compute_data_type AND operation-specific enum/scalar attributes (forward_phase, etc.) — not just tensor UIDs
- [ ] Backend graph tests verify compute_data_type AND enum/scalar attrs AND tensor UIDs in deserialized graph
- [ ] Integration tests verify full frontend→backend→serialize→deserialize→verify pipeline
- [ ] Integration tests have both explicit UID and auto-assigned UID test cases
- [ ] Integration tests have an **inference/no-optional-tensor** round-trip test that verifies optional tensor fields are `nullopt` (not just absent) in deserialized graph
- [ ] Optional tensor validation in integration tests checks uid, dims, strides, data_type — NOT just name
- [ ] Integration tests in TRAINING mode do NOT have unnecessary `if(mean)` / `if(invVariance)` guards — training always produces these; use `ASSERT_NE(mean, nullptr)` instead
- [ ] Test naming: file name convention (e.g. `LayerNorm`) is consistent with class/test names inside (no mismatch like `Layernorm` vs `LayerNorm`)
- [ ] Test tensor dimensions are valid for the operation (ranks match, inner dims compatible)

#### Enum Convention
- [ ] ALL new enums use `_EXT` suffix
- [ ] Descriptor type: `HIPDNN_BACKEND_OPERATION_{{NODE_UPPER}}_DESCRIPTOR_EXT`
- [ ] All attributes: `HIPDNN_ATTR_OPERATION_{{NODE_UPPER}}_*_EXT`
- [ ] Compute type: `HIPDNN_ATTR_{{NODE_UPPER}}_COMP_TYPE_EXT`
- [ ] Enum range doesn't conflict with existing ranges
- [ ] String utils and tests use `_EXT` consistently

#### Code Quality
- [ ] No new utility functions that duplicate existing ones in DescriptorAttributeUtils or DescriptorHelpers
- [ ] No hardcoded constants in test files (uses test_sdk constants)
- [ ] Follows existing code style and conventions
- [ ] No unused includes or dead code
- [ ] Error messages are descriptive and include class/method name
- [ ] Doc comment in HipdnnBackendAttributeName.h lists the new attribute range
- [ ] CMakeLists.txt source entries are sorted alphabetically
- [ ] `flatbuffers::Optional<T>` fields use local variable pattern (not address-of temporary)

### 5. Cross-Reference with Matmul Implementation

Compare the diff against the matmul reference to ensure nothing was missed:
```bash
git -C {{worktree_path}} diff origin/develop...origin/users/sareeder/almiopen-1121/add-matmul-descriptor --name-only -- projects/hipdnn/
```

For each file in the matmul reference, verify there's a corresponding file for this node (where applicable).

### 6. Standard Code Review

Also review for:
- **Bugs, logic errors, resource leaks**
- **Security issues** (injection, hardcoded secrets)
- **Error handling gaps** (unchecked returns, swallowed exceptions)
- **Performance concerns** (unnecessary allocations)
- **Missing edge cases** (null inputs, overflow, boundaries)
- **API consistency** with existing descriptors

### 7. Classify Findings

- **Critical** — Missing file, missing test, wrong enum, likely bug, missing `_EXT` suffix, unmet acceptance criterion. Must fix.
- **Warning** — Potential issue, incomplete coverage, code smell. Should address.
- **Suggestion** — Style, minor optimization. Optional.

### 8. Output Verdict

```
## Review Verdict: PASS | FAIL

### File Completeness
<checklist from section 3 with PASS/FAIL for each>

### Critical
<numbered list or "None found.">

### Warnings
<numbered list or "None found.">

### Suggestions
<numbered list or "None found.">

### Acceptance Criteria Check
<checklist with PASS/FAIL for each>

### Summary
<overall assessment>
```

**Verdict rules:**
- **FAIL** if any Critical or Warning findings exist
- **FAIL** if any required file is missing
- **FAIL** if any `_EXT` suffix is missing from new enums
- **PASS** if only Suggestions or no findings

### 9. Record in Beads

```bash
source "$HOME/.cargo/env" && br comments add {{beads_id}} "REVIEW: <PASS|FAIL> - <brief summary>"
```

## Rules

- Do NOT modify any files. This is a read-only review.
- Use absolute paths for all operations.
- Be thorough — the checklist is the minimum bar. Flag anything else you find.
- Be fair — only flag real issues, not style preferences (pre-commit handles formatting).

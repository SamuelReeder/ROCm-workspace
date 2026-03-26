# Descriptor Lifting Review Agent

You are reviewing the implementation of descriptor-based lifting for the **{{NodePascal}}** operation in hipDNN.

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

### 3. Descriptor Lifting File Completeness Check

This is the most critical part. Verify ALL required changes exist and are properly implemented:

#### Files That MUST Be Created

- [ ] **Frontend unpacker**: `projects/hipdnn/frontend/include/hipdnn_frontend/detail/{{NodePascal}}Unpacker.hpp`
- [ ] **fromNode tests**: `projects/hipdnn/backend/tests/descriptors/Test{{NodePascal}}OperationFromNode.cpp`

#### Files That MUST Be Modified

- [ ] **Backend descriptor header**: `projects/hipdnn/backend/src/descriptors/{{NodePascal}}OperationDescriptor.hpp` (fromNode decl, _name member, includes)
- [ ] **Backend descriptor impl**: `projects/hipdnn/backend/src/descriptors/{{NodePascal}}OperationDescriptor.cpp` (fromNode impl, name/type attr handling, buildNode name)
- [ ] **NodeFactory header**: `projects/hipdnn/backend/src/descriptors/NodeFactory.hpp` (uncommented include)
- [ ] **NodeFactory impl**: `projects/hipdnn/backend/src/descriptors/NodeFactory.cpp` (uncommented case)
- [ ] **OperationUnpacker**: `projects/hipdnn/frontend/include/hipdnn_frontend/detail/OperationUnpacker.hpp` (uncommented include + case)
- [ ] **Frontend node**: `projects/hipdnn/frontend/include/hipdnn_frontend/node/{{NodePascal}}Node.hpp` (unpack_from_descriptor override + unpacker include)
- [ ] **Backend tests CMake**: `projects/hipdnn/backend/tests/CMakeLists.txt` (fromNode test entry)

#### Files That MUST NOT Exist

- [ ] No `fragments/` directory in `projects/hipdnn/` — fragment files must be deleted after applying

### 4. Implementation Quality Checks

For each file, verify:

#### Backend Descriptor Changes (`{{NodePascal}}OperationDescriptor.hpp/.cpp`)

- [ ] `fromNode()` is declared as `static std::shared_ptr<{{NodePascal}}OperationDescriptor>`
- [ ] `fromNode()` takes `const NodeT&` and `const unordered_map<int64_t, shared_ptr<TensorDescriptor>>&`
- [ ] `fromNode()` resolves ALL tensor UIDs from the tensorMap
- [ ] `fromNode()` throws on missing required tensors
- [ ] `fromNode()` copies ALL data fields from the FlatBuffer attributes
- [ ] `fromNode()` sets compute data type from `nodeT.compute_data_type`
- [ ] `fromNode()` sets name from `nodeT.name`
- [ ] `fromNode()` calls base class `finalize()` (NOT the derived override)
- [ ] `_name` member declared as `std::string`
- [ ] `<unordered_map>` included in header
- [ ] `setAttribute()` handles `HIPDNN_ATTR_OPERATION_NAME_EXT` with `HIPDNN_TYPE_CHAR`
- [ ] `setAttribute()` name handling strips trailing null
- [ ] `getAttribute()` handles `HIPDNN_ATTR_OPERATION_NAME_EXT` — returns `size + 1` for null terminator
- [ ] `getAttribute()` handles `HIPDNN_ATTR_OPERATION_TYPE_EXT` — returns correct `HIPDNN_OPERATION_TYPE_{{NODE_UPPER}}`
- [ ] `getAttribute()` uses `HIPDNN_TYPE_OPERATION_TYPE_EXT` type tag for operation type
- [ ] `buildNode()` sets `node->name = _name`
- [ ] Uses `checkSetArgs`/`checkGetArgs` for type validation

#### Frontend Unpacker (`{{NodePascal}}Unpacker.hpp`)

- [ ] Uses `unpackAndRegisterTensor()` for ALL tensor fields
- [ ] Uses `getDescriptorAttrScalar()` for scalar/mode/enum fields with correct types
- [ ] Uses `getDescriptorAttrVec()` for vector fields
- [ ] Uses `unpackGraphDataType()` for compute data type
- [ ] Uses `getDescriptorAttrString()` for operation name
- [ ] Sets attributes on the frontend attributes object via correct setters
- [ ] Mode fields use inverse converter functions (e.g., `toFrontendConvMode`)
- [ ] Returns `Error{}` on success, propagates errors via `HIPDNN_CHECK_ERROR`

#### Frontend Node (`{{NodePascal}}Node.hpp`)

- [ ] `unpack_from_descriptor()` override exists with correct signature
- [ ] Delegates to the unpacker function with correct arguments
- [ ] Unpacker include is present

#### Scaffolding Uncomment

- [ ] NodeFactory.hpp — include for `{{NodePascal}}OperationDescriptor.hpp` is uncommented
- [ ] NodeFactory.cpp — switch case for this node is uncommented
- [ ] OperationUnpacker.hpp — include for node header is uncommented
- [ ] OperationUnpacker.hpp — switch case for this operation type is uncommented
- [ ] Only THIS node's entries are uncommented (other nodes remain commented)

#### fromNode Test Quality

- [ ] Test uses constants from `test_sdk/constants/{{NodePascal}}Constants.hpp` (NOT inline values)
- [ ] `CreatesValidFinalizedDescriptor` — verifies non-null, finalized, correct type
- [ ] `NodeFactoryDelegatesCorrectly` — verifies NodeFactory dispatches to fromNode, checks all attributes via static_pointer_cast
- [ ] `PreservesComputeDataType` — tests with non-default type (e.g., HALF)
- [ ] `SetsTensorReferences` — verifies all tensor UIDs via getter
- [ ] `TensorReferencesMatchTensorMap` — verifies shared_ptr identity (pointer comparison, NOT UID)
- [ ] `FailsWithMissing<Tensor>Tensor` — one per required tensor, verifies correct exception
- [ ] `GetTensorDescriptorsReturnsAllTensors` — verifies count and UID order
- [ ] `BuildNodeRoundTrip` — verifies compute_data_type, attributes type, and all field values in rebuilt node
- [ ] `GetAttributeWorksAfterFromNode` — verifies getAttribute on fromNode-created descriptor (vectors, compute type, modes, tensors, operation type)
- [ ] `NamePreservedFromNode` — verifies name with specific non-empty value
- [ ] `EmptyNamePreservedFromNode` — verifies empty name yields count=1 (null terminator only)
- [ ] `BuildNodePreservesName` — verifies name in rebuilt node
- [ ] If mode/enum fields: `PreservesMode`/`PreservesEnum` tests with alternate values
- [ ] If vector/scalar fields: `PreservesDataFields` test
- [ ] Test file includes all necessary headers (especially `HipdnnOperationType.h` for operation type assertions)

#### Code Quality

- [ ] No fragment files remain in `projects/hipdnn/fragments/`
- [ ] No new utility functions that duplicate existing ones
- [ ] No hardcoded constants in test files
- [ ] CMakeLists.txt entries sorted alphabetically
- [ ] Follows existing code style and conventions
- [ ] Error messages are descriptive and include class/method name

### 5. Cross-Reference with ConvolutionFwd Lifting

Compare the changes against the ConvolutionFwd reference:
```bash
git -C {{worktree_path}} fetch origin users/bharriso/descriptor-codegen 2>/dev/null
git -C {{worktree_path}} show origin/users/bharriso/descriptor-codegen:projects/hipdnn/backend/src/descriptors/ConvolutionFwdOperationDescriptor.cpp | grep -A 50 "fromNode"
```

For each pattern in the ConvFwd reference, verify there's a corresponding pattern for this node.

### 6. Standard Code Review

Also review for:
- **Bugs, logic errors, resource leaks**
- **Error handling gaps** (unchecked returns, swallowed exceptions)
- **Missing edge cases** (null inputs, missing tensors)
- **API consistency** with existing descriptors

### 7. Classify Findings

- **Critical** — Missing file, missing test, wrong operation type, missing scaffolding uncomment, likely bug, unmet acceptance criterion. Must fix.
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
- **FAIL** if any required file is missing or any scaffolding entry not uncommented
- **FAIL** if fromNode tests are incomplete
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

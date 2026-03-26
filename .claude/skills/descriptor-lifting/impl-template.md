# Descriptor Lifting Implementation Agent

You are implementing descriptor-based lifting for the **{{NodePascal}}** operation in hipDNN. Lifting is the inverse of lowering — it reconstructs frontend graph attributes from serialized FlatBuffer data via `fromNode()` on the backend descriptor and `unpack_from_descriptor()` on the frontend node.

**Work autonomously.** Do NOT ask the user for confirmation or approval. If you have a question, resolve it by reading the ConvolutionFwd lifting reference on branch `origin/users/bharriso/descriptor-codegen` or by examining existing code patterns in the worktree.

## Context

- **Worktree**: {{worktree_path}}
- **Branch**: {{branch}}
- **Jira Key**: {{jira_key}}
- **Beads Task**: {{beads_id}}
- **Node Type**: {{NodePascal}} (snake: `{{node_snake}}`, UPPER: `{{NODE_UPPER}}`)

## Jira Description

{{jira_description}}

## Acceptance Criteria

{{acceptance_criteria}}

## Additional Instructions

{{additional_instructions}}

## What Already Exists

{{existing_files}}

## Codegen Output

The codegen tool has already been run by the orchestrator with `--lift-only`. The following files/fragments were generated and placed in the worktree. **Start from these generated files** — review them, fix any issues, and then complete the remaining manual integration work.

{{codegen_output}}

## Descriptor Lifting Additions

The codegen also produced a `descriptor_lifting_additions.txt` file that describes the exact changes needed to the existing descriptor `.hpp` and `.cpp` files. Apply these changes.

{{descriptor_lifting_additions}}

## Reference Implementation

The ConvolutionFwd lifting is the canonical reference. It is fully implemented on `origin/users/bharriso/descriptor-codegen`. Key files:

```bash
git -C {{worktree_path}} show origin/users/bharriso/descriptor-codegen:projects/hipdnn/backend/src/descriptors/ConvolutionFwdOperationDescriptor.hpp
git -C {{worktree_path}} show origin/users/bharriso/descriptor-codegen:projects/hipdnn/backend/src/descriptors/ConvolutionFwdOperationDescriptor.cpp
git -C {{worktree_path}} show origin/users/bharriso/descriptor-codegen:projects/hipdnn/frontend/include/hipdnn_frontend/detail/ConvFpropUnpacker.hpp
git -C {{worktree_path}} show origin/users/bharriso/descriptor-codegen:projects/hipdnn/frontend/include/hipdnn_frontend/node/ConvolutionFpropNode.hpp
```

Also check the codegen CLAUDE.md for the full lifting workflow documentation:
```bash
git -C {{worktree_path}} show origin/users/bharriso/descriptor-codegen:projects/hipdnn/tools/DescriptorGenerator/CLAUDE.md
```

## Node's Frontend Attributes

{{node_frontend_attributes}}

---

# IMPLEMENTATION GUIDE

The codegen `--lift-only` has generated the unpacker, fromNode test, and fragment files. Your job is to:
1. **Review the codegen output** — check what was generated and fix any issues
2. **Apply the descriptor_lifting_additions.txt** — modify the existing descriptor `.hpp` and `.cpp` to add `fromNode()`, `_name` member, and operation name/type handling
3. **Place generated files** — put the unpacker and fromNode test in the correct locations
4. **Uncomment scaffolding entries** — in NodeFactory.cpp/.hpp and OperationUnpacker.hpp
5. **Wire the frontend node** — add `unpack_from_descriptor()` override and unpacker include
6. **Apply fragment files** — insert NodeFactory case, OperationUnpacker case, operation type enum, node unpack override
7. **Delete fragment files** after applying them — they are scaffolding and must NOT be committed
8. **Update CMake** — add the new test file
9. **Follow the steps below** for anything not already handled by codegen

For each step, first check if codegen already produced the file. If so, review and fix it. If not, create it following the patterns below. **Read the ConvolutionFwd reference files** on the codegen branch for exact patterns.

## Pre-commit Rule

**Before every commit**, run pre-commit:
```bash
cd {{worktree_path}} && git add <files> && pre-commit run
```
If pre-commit modifies files, re-stage and commit. If it reports unfixable errors, fix them manually and re-run.

---

## Step 1: Understand What Exists

Read the node's existing descriptor implementation (from the lowering PR) to understand what's already there:
```
Read: {{worktree_path}}/projects/hipdnn/backend/src/descriptors/{{NodePascal}}OperationDescriptor.hpp
Read: {{worktree_path}}/projects/hipdnn/backend/src/descriptors/{{NodePascal}}OperationDescriptor.cpp
Read: {{worktree_path}}/projects/hipdnn/frontend/include/hipdnn_frontend/node/{{NodePascal}}Node.hpp
Read: {{worktree_path}}/projects/hipdnn/frontend/include/hipdnn_frontend/attributes/{{NodePascal}}Attributes.hpp
```

Also read the frontend unpacker helpers:
```
Read: {{worktree_path}}/projects/hipdnn/frontend/include/hipdnn_frontend/detail/DescriptorUnpackHelpers.hpp
```

Identify:
- **All tensors** and their attribute enum names
- **All data fields** (scalars, vectors, enums/modes)
- **Compute data type** attribute name
- **Optional tensors** and how they're handled

---

## Step 2: Apply Descriptor Lifting Additions

The `descriptor_lifting_additions.txt` file describes exact changes to make to the existing descriptor files. Apply them carefully.

### 2a. Header Changes (`{{NodePascal}}OperationDescriptor.hpp`)

Add these to the header:

1. Include `<unordered_map>` and `<memory>`
2. Add `static fromNode()` factory method declaration:
```cpp
static std::shared_ptr<{{NodePascal}}OperationDescriptor> fromNode(
    const hipdnn_data_sdk::data_objects::NodeT& nodeT,
    const std::unordered_map<int64_t, std::shared_ptr<TensorDescriptor>>& tensorMap);
```
3. Add `_name` member:
```cpp
std::string _name;
```

### 2b. Implementation Changes (`{{NodePascal}}OperationDescriptor.cpp`)

Add these to the implementation:

1. **`setAttribute()`** — add cases for:
   - `HIPDNN_ATTR_OPERATION_NAME_EXT`: store the name string
   ```cpp
   case HIPDNN_ATTR_OPERATION_NAME_EXT:
       checkSetArgs(attributeType, HIPDNN_TYPE_CHAR, "{{NodePascal}}OperationDescriptor::setAttribute");
       _name = std::string(static_cast<const char*>(arrayOfElements),
                          static_cast<size_t>(elementCount));
       // Remove trailing null if present
       if(!_name.empty() && _name.back() == '\0')
           _name.pop_back();
       break;
   ```

2. **`getAttribute()`** — add cases for:
   - `HIPDNN_ATTR_OPERATION_NAME_EXT`: return the name string
   ```cpp
   case HIPDNN_ATTR_OPERATION_NAME_EXT:
       checkGetArgs(attributeType, HIPDNN_TYPE_CHAR, "{{NodePascal}}OperationDescriptor::getAttribute");
       *elementCount = static_cast<int64_t>(_name.size() + 1); // +1 for null terminator
       if(requestedElementCount > 0 && arrayOfElements != nullptr)
       {
           auto copyLen = std::min(static_cast<size_t>(requestedElementCount), _name.size() + 1);
           std::memcpy(arrayOfElements, _name.c_str(), copyLen);
       }
       break;
   ```
   - `HIPDNN_ATTR_OPERATION_TYPE_EXT`: return the operation type
   ```cpp
   case HIPDNN_ATTR_OPERATION_TYPE_EXT:
       checkGetArgs(attributeType, HIPDNN_TYPE_OPERATION_TYPE_EXT,
                    "{{NodePascal}}OperationDescriptor::getAttribute");
       *elementCount = 1;
       if(requestedElementCount > 0 && arrayOfElements != nullptr)
       {
           *static_cast<hipdnnOperationType_t*>(arrayOfElements)
               = HIPDNN_OPERATION_TYPE_{{NODE_UPPER}};
       }
       break;
   ```

3. **`buildNode()`** — add name to the built node:
   ```cpp
   node->name = _name;
   ```

4. **`toString()`** — add name to the debug string if non-empty.

5. **`fromNode()` implementation** — the full static factory method. Read the codegen-generated `descriptor_lifting_additions.txt` for the exact implementation, or follow the ConvolutionFwd reference:
   ```cpp
   std::shared_ptr<{{NodePascal}}OperationDescriptor>
   {{NodePascal}}OperationDescriptor::fromNode(
       const hipdnn_data_sdk::data_objects::NodeT& nodeT,
       const std::unordered_map<int64_t, std::shared_ptr<TensorDescriptor>>& tensorMap)
   {
       const auto* attrs = nodeT.attributes.As{{FbsTable}}();
       THROW_IF_NULL(attrs, HIPDNN_STATUS_INTERNAL_ERROR,
                     "{{NodePascal}}OperationDescriptor::fromNode: missing attributes");

       auto desc = std::make_shared<{{NodePascal}}OperationDescriptor>();

       // Set tensors from UID map
       auto findTensor = [&](int64_t uid, const char* name) {
           auto it = tensorMap.find(uid);
           THROW_IF_TRUE(it == tensorMap.end(), HIPDNN_STATUS_INTERNAL_ERROR,
                         std::string("{{NodePascal}}::fromNode: missing tensor ") + name);
           return it->second;
       };

       desc->_<tensor1>Desc = findTensor(attrs-><tensor1>_tensor_uid, "<tensor1>");
       desc->_data.<tensor1>_tensor_uid = attrs-><tensor1>_tensor_uid;
       // ... repeat for all tensors

       // Set data fields
       // desc->_data.<field> = attrs-><field>;  // for each data field

       // Set compute data type
       desc->_computeDataType = nodeT.compute_data_type;

       // Set name
       desc->_name = nodeT.name;

       desc->HipdnnBackendDescriptorImpl<{{NodePascal}}OperationDescriptor>::finalize();
       return desc;
   }
   ```

**CRITICAL**: The codegen generates the exact `fromNode()` implementation tailored to this node's fields. Use the codegen output — don't hand-write it unless the codegen version has issues.

**Commit**: "Add {{NodePascal}} descriptor lifting support (fromNode, name/type attrs)"

---

## Step 3: Place Generated Unpacker

**File**: `projects/hipdnn/frontend/include/hipdnn_frontend/detail/{{NodePascal}}Unpacker.hpp`

The codegen `--lift-only` generates this file. Place it in the correct location if not already there.

Review it to ensure:
- All tensors are unpacked via `unpackAndRegisterTensor()`
- All data fields are unpacked via the correct helper (`getDescriptorAttrScalar`, `getDescriptorAttrVec`, etc.)
- Mode/enum fields use the correct inverse converter function
- Compute data type is unpacked via `unpackGraphDataType()`
- Operation name is unpacked via `getDescriptorAttrString()`

**Commit**: "Add {{NodePascal}} frontend unpacker for descriptor lifting"

---

## Step 4: Uncomment Scaffolding Entries

The lifting scaffolding branch pre-populated commented-out entries in shared files. Uncomment the entries for this node.

### 4a. NodeFactory.hpp

**File**: `projects/hipdnn/backend/src/descriptors/NodeFactory.hpp`

Find the commented-out include for this node's descriptor and uncomment it:
```cpp
// Before:
// #include "{{NodePascal}}OperationDescriptor.hpp"
// After:
#include "{{NodePascal}}OperationDescriptor.hpp"
```

### 4b. NodeFactory.cpp

**File**: `projects/hipdnn/backend/src/descriptors/NodeFactory.cpp`

Find the commented-out case for this node and uncomment it:
```cpp
// Before:
// case NodeAttributes::{{FbsTable}}:
//     return {{NodePascal}}OperationDescriptor::fromNode(nodeT, tensorMap);
// After:
case NodeAttributes::{{FbsTable}}:
    return {{NodePascal}}OperationDescriptor::fromNode(nodeT, tensorMap);
```

### 4c. OperationUnpacker.hpp

**File**: `projects/hipdnn/frontend/include/hipdnn_frontend/detail/OperationUnpacker.hpp`

Find the commented-out include and switch case for this node and uncomment both:
```cpp
// Uncomment the include at the top:
#include <hipdnn_frontend/node/{{NodePascal}}Node.hpp>

// Uncomment the case in the switch:
case HIPDNN_OPERATION_TYPE_{{NODE_UPPER}}:
    return {std::make_shared<graph::{{NodePascal}}Node>(graph::{{NodePascal}}Attributes{}, graphAttrs), {}};
```

**IMPORTANT**: The exact node class name and attributes class name may differ from the simple pattern above. Check the actual commented-out code in OperationUnpacker.hpp — it was generated from the correct class names. Use what's already there.

**Commit**: "Uncomment {{NodePascal}} lifting scaffolding entries"

---

## Step 5: Wire Frontend Node

**File**: `projects/hipdnn/frontend/include/hipdnn_frontend/node/{{NodePascal}}Node.hpp`

Add the unpacker include and the `unpack_from_descriptor()` override:

1. Add include at top:
```cpp
#include <hipdnn_frontend/detail/{{NodePascal}}Unpacker.hpp>
```

2. Add the override method to the node class:
```cpp
Error unpack_from_descriptor(
    hipdnnBackendDescriptor_t opDesc,
    std::unordered_map<int64_t, std::shared_ptr<graph::TensorAttributes>>& tensorMap) override
{
    return detail::{{unpacker_function}}(opDesc, tensorMap, attributes);
}
```

The `{{unpacker_function}}` name comes from the codegen output (e.g., `unpackConvFprop`, `unpackMatmul`). Check the generated unpacker file for the exact function name.

**Commit**: "Wire {{NodePascal}}Node::unpack_from_descriptor to unpacker"

---

## Step 6: Place and Verify fromNode Tests

**File**: `projects/hipdnn/backend/tests/descriptors/Test{{NodePascal}}OperationFromNode.cpp`

The codegen `--lift-only` generates this file. Place it in the correct location if not already there.

The generated test file should include:
- `CreatesValidFinalizedDescriptor` — basic fromNode lifecycle
- `NodeFactoryDelegatesCorrectly` — verifies NodeFactory dispatches to fromNode
- `PreservesComputeDataType` — verifies compute type survives round-trip
- `PreservesMode` (if applicable) — verifies mode/enum fields survive round-trip
- `PreservesDataFields` (if applicable) — verifies vector/scalar fields survive round-trip
- `SetsTensorReferences` — verifies tensor UIDs are correctly resolved
- `TensorReferencesMatchTensorMap` — verifies shared_ptr identity with the tensorMap
- `FailsWithMissing<Tensor>Tensor` — one per required tensor
- `GetTensorDescriptorsReturnsAllTensors` — verifies tensor ordering
- `BuildNodeRoundTrip` — verifies fromNode → buildNode round-trip preserves all attributes
- `GetAttributeWorksAfterFromNode` — verifies getAttribute on fromNode-created descriptor
- `NamePreservedFromNode` — verifies operation name survives round-trip
- `EmptyNamePreservedFromNode` — verifies empty name case
- `BuildNodePreservesName` — verifies name in rebuilt node

**IMPORTANT**: If the test uses test_sdk constants, verify the constants file exists and has the correct values. If not, the constants should already exist from the lowering PR.

**Commit**: "Add {{NodePascal}} fromNode round-trip tests"

---

## Step 7: CMake Updates

### 7a. Backend tests
**File**: `projects/hipdnn/backend/tests/CMakeLists.txt`
Add: `descriptors/Test{{NodePascal}}OperationFromNode.cpp`

Keep entries sorted alphabetically.

**Commit**: "Update CMakeLists.txt for {{NodePascal}} lifting tests"

---

## Step 8: Clean Up Fragment Files

Delete all fragment files from the worktree:
```bash
rm -rf {{worktree_path}}/projects/hipdnn/fragments/
```

Do NOT commit fragment files.

---

# KNOWN PITFALLS

1. **Scaffolding must be present**: The lifting scaffolding branch must have been merged to develop before this work. If `HipdnnOperationType.h` doesn't have the `HIPDNN_OPERATION_TYPE_{{NODE_UPPER}}` enum value, the scaffolding hasn't landed yet — report this to the orchestrator.

2. **Lowering must exist first**: The descriptor `.hpp`/`.cpp`, packer, test constants, etc. must already exist from the lowering PR. If they don't exist, lifting cannot proceed.

3. **fromNode() skips finalize validation**: `fromNode()` calls `HipdnnBackendDescriptorImpl::finalize()` directly (the base class method), NOT the derived `finalize()` override. This is intentional — the data coming from FlatBuffer is already validated. Use the base class finalize to set the finalized flag.

4. **Operation type enum**: The operation type must match what's defined in `HipdnnOperationType.h`. Check the scaffolding for the exact value.

5. **Unpacker function naming**: The codegen derives the unpacker function name from the YAML config's `frontend.unpacker_function` field. The function name in the generated unpacker file must match what's used in the node's `unpack_from_descriptor()` override.

6. **OperationUnpacker node construction**: The OperationUnpacker creates a new node with default-constructed attributes, then calls `unpack_from_descriptor()` to populate them. The attributes class must have a default constructor.

7. **HIPDNN_TYPE_OPERATION_TYPE_EXT**: When returning the operation type in `getAttribute()`, use `HIPDNN_TYPE_OPERATION_TYPE_EXT` as the type tag, not `HIPDNN_TYPE_INT64`.

8. **Include guards**: The generated files use `#pragma once`. No additional include guards needed.

9. **Test constants reuse**: The fromNode tests should use the same test constants from `test_sdk/constants/{{NodePascal}}Constants.hpp` that the lowering tests use. Do NOT create new constants.

10. **`checkSetArgs`/`checkGetArgs`**: Use these existing helpers from the base descriptor class for type validation in the new setAttribute/getAttribute cases.

11. **CMakeLists.txt sorting**: Keep entries sorted alphabetically.

---

# COMPLETION CHECKLIST

Before reporting completion, verify ALL of these:

- [ ] Backend descriptor header has `fromNode()` declaration
- [ ] Backend descriptor header has `_name` member
- [ ] Backend descriptor header has `<unordered_map>` and `<memory>` includes
- [ ] Backend descriptor implementation has `fromNode()` with correct tensor/field mapping
- [ ] `fromNode()` calls base class `finalize()` (not derived override)
- [ ] `setAttribute()` handles `HIPDNN_ATTR_OPERATION_NAME_EXT` (HIPDNN_TYPE_CHAR)
- [ ] `getAttribute()` handles `HIPDNN_ATTR_OPERATION_NAME_EXT` (returns size+1 for null terminator)
- [ ] `getAttribute()` handles `HIPDNN_ATTR_OPERATION_TYPE_EXT` (returns correct operation type)
- [ ] `buildNode()` sets `node->name = _name`
- [ ] Frontend unpacker file placed at correct location
- [ ] Unpacker uses correct helpers (`unpackAndRegisterTensor`, `getDescriptorAttrScalar`, etc.)
- [ ] Unpacker unpacks operation name via `getDescriptorAttrString`
- [ ] NodeFactory.hpp — include uncommented
- [ ] NodeFactory.cpp — switch case uncommented
- [ ] OperationUnpacker.hpp — include and switch case uncommented
- [ ] Frontend node has `#include` for unpacker
- [ ] Frontend node has `unpack_from_descriptor()` override calling the unpacker
- [ ] fromNode tests placed at correct location
- [ ] fromNode tests cover: lifecycle, NodeFactory delegation, data type, mode, tensors, name, round-trip
- [ ] Backend tests CMakeLists.txt updated with fromNode test (sorted alphabetically)
- [ ] Fragment files deleted (no `fragments/` directory in worktree)
- [ ] Pre-commit passed on every commit
- [ ] Reuses existing test_sdk constants from lowering (no new constants files)
- [ ] All includes correctly added

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

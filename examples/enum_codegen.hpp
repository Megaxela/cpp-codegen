#pragma once

namespace some::cool {
/**
 * @brief This enumeration should be ignored for codegen.
 */
enum class enum_class_ignored {
    enum_class_ignored_val_1,
    enum_class_ignored_val_2,
};

/**
 * @brief This enumeration shows sample conversion of enum class.
 * @cpp_codegen
 * string_serialization
 * json_serialization
 */
enum class enum_class_simple {
    enum_class_simple_val_1,
    enum_class_simple_val_2,
};

/**
 * @brief This enumeration shows sample conversion of simple enum.
 * @cpp_codegen
 * string_serialization
 * json_serialization
 */
enum enum_simple {
    enum_simple_val_1,
    enum_simple_val_2,
};

/**
 * @brief This enumeration shows codegen custom string value.
 * @cpp_codegen
 * string_serialization
 */
enum class enum_custom_string {
    enum_custom_string_val_1,  //< "val_1_str"s
    enum_custom_string_val_2,  //< "val_2_str"s
};
/**
 * @brief This enumeration shows codegen custom json value.
 * @cpp_codegen
 * json_serialization
 */
enum class enum_custom_json {
    enum_custom_json_val_1,  //< "val_1_json"json
    enum_custom_json_val_2,  //< "val_2_json"json
};

/**
 * @brief This enumeration shows codegen custom combined values.
 * @cpp_codegen
 * string_serialization
 * json_serialization
 */
enum class enum_custom_combined {
    enum_custom_combined_val_1,  //< "val_1_comb_string"s "val_1_comb_json"json
    enum_custom_combined_val_2,  //< "val_2_comb_string"s
                                 //< "val_2_comb_json"json
};

namespace internal {
/**
 * @brief This enumeration shows namespaces support.
 * @cpp_codegen
 * string_serialization
 */
enum class enum_simple_internal {
    enum_simple_internal_val_1,  //
    enum_simple_internal_val_2,  //
};
}  // namespace internal

class parent_class {
public:
    /**
     * @brief This enumeration shows internal class support.
     * @cpp_codegen
     * string_serialization.
     */
    enum class enum_simple_member {
        enum_simple_member_val_1,  //
        enum_simple_member_val_2,  //
    };
};
}  // namespace some::cool

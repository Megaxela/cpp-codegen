#include <gtest/gtest.h>

#include <converters/enum_custom_combined.hpp>

TEST(enum_custom_combined, to_string) {
    ASSERT_EQ(
        to_string(some::cool::enum_custom_combined::enum_custom_combined_val_1),
        "val_1_comb_string");
    ASSERT_EQ(
        to_string(some::cool::enum_custom_combined::enum_custom_combined_val_2),
        "val_2_comb_string");
}

TEST(enum_custom_combined, to_json) {
    ASSERT_EQ(nlohmann::json(
                  some::cool::enum_custom_combined::enum_custom_combined_val_1),
              "val_1_comb_json");
    ASSERT_EQ(nlohmann::json(
                  some::cool::enum_custom_combined::enum_custom_combined_val_2),
              "val_2_comb_json");
}

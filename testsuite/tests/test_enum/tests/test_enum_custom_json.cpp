#include <gtest/gtest.h>

#include <converters/enum_custom_json.hpp>

TEST(enum_custom_json, to_json) {
    ASSERT_EQ(
        nlohmann::json(some::cool::enum_custom_json::enum_custom_json_val_1),
        "val_1_json");
    ASSERT_EQ(
        nlohmann::json(some::cool::enum_custom_json::enum_custom_json_val_2),
        "val_2_json");
}

#include <gtest/gtest.h>

#include <converters/enum_custom_string.hpp>

TEST(enum_custom_string, to_string) {
    ASSERT_EQ(
        to_string(some::cool::enum_custom_string::enum_custom_string_val_1),
        "val_1_str");
    ASSERT_EQ(
        to_string(some::cool::enum_custom_string::enum_custom_string_val_2),
        "val_2_str");
}

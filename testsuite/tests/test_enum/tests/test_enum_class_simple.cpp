#include <gtest/gtest.h>

#include <converters/enum_class_simple.hpp>

TEST(enum_class_simple, to_string) {
    ASSERT_EQ(to_string(some::cool::enum_class_simple::enum_class_simple_val_1),
              "enum_class_simple_val_1");
    ASSERT_EQ(to_string(some::cool::enum_class_simple::enum_class_simple_val_2),
              "enum_class_simple_val_2");
}

TEST(enum_class_simple, to_json) {
    ASSERT_EQ(
        nlohmann::json(some::cool::enum_class_simple::enum_class_simple_val_1),
        "enum_class_simple_val_1");
    ASSERT_EQ(
        nlohmann::json(some::cool::enum_class_simple::enum_class_simple_val_2),
        "enum_class_simple_val_2");
}

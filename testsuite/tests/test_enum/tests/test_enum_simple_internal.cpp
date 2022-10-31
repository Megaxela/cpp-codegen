#include <gtest/gtest.h>

#include <converters/enum_simple_internal.hpp>

TEST(enum_simple_internal, to_string) {
    ASSERT_EQ(to_string(some::cool::internal::enum_simple_internal::
                            enum_simple_internal_val_1),
              "enum_simple_internal_val_1");
    ASSERT_EQ(to_string(some::cool::internal::enum_simple_internal::
                            enum_simple_internal_val_2),
              "enum_simple_internal_val_2");
}

TEST(enum_simple_internal, to_json) {
    ASSERT_EQ(nlohmann::json(some::cool::internal::enum_simple_internal::
                                 enum_simple_internal_val_1),
              "enum_simple_internal_val_1");
    ASSERT_EQ(nlohmann::json(some::cool::internal::enum_simple_internal::
                                 enum_simple_internal_val_2),
              "enum_simple_internal_val_2");
}

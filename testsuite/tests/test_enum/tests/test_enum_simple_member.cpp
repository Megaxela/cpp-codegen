#include <gtest/gtest.h>

#include <converters/enum_simple_member.hpp>

TEST(enum_simple_member, to_string) {
    ASSERT_EQ(to_string(some::cool::parent_class::enum_simple_member::
                            enum_simple_member_val_1),
              "enum_simple_member_val_1");
    ASSERT_EQ(to_string(some::cool::parent_class::enum_simple_member::
                            enum_simple_member_val_2),
              "enum_simple_member_val_2");
}

TEST(enum_simple_member, to_json) {
    ASSERT_EQ(nlohmann::json(some::cool::parent_class::enum_simple_member::
                                 enum_simple_member_val_1),
              "enum_simple_member_val_1");
    ASSERT_EQ(nlohmann::json(some::cool::parent_class::enum_simple_member::
                                 enum_simple_member_val_2),
              "enum_simple_member_val_2");
}

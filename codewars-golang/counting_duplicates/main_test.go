package main

import (
	"testing"
)

func TestDuplicateCount(t *testing.T) {
	fixtures := []struct {
		input    string
		expected int
	}{
		{"abcde", 0},
		{"aabbcde", 2},
		{"aabBcde", 2},
		{"indivisibility", 1},
		{"Indivisibilities", 2},
		{"aA11", 2},
		{"ABBA", 2},
	}

	for _, testCase := range fixtures {
		t.Run(testCase.input, func(t *testing.T) {
			actual := duplicate_count(testCase.input)
			if actual != testCase.expected {
				t.Errorf(
					"duplicate_count(%q) = %d, want %d",
					testCase.input, actual, testCase.expected,
				)
			}
		})
	}
}

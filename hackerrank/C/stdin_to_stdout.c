#include <stdio.h>
#include <stdlib.h>

#define ARRAY_LIMIT 256
int main(void)
{
    char single_char_input;
    char row_input[ARRAY_LIMIT] = "";
    char sentence[ARRAY_LIMIT] = "";

    if (scanf("%c", &single_char_input) != 1)
    {
        printf("Error reading single char input\n");
        return EXIT_FAILURE;
    }
    if (scanf("%255s", row_input) != 1)
    {
        printf("Error reading row input\n");
        return EXIT_FAILURE;
    }
    scanf("\n");
    if (scanf("%255[^\n]%*c", sentence) != 1)
    {
        printf("Error reading sentence input\n");
        return EXIT_FAILURE;
    }

    char print_buffer[ARRAY_LIMIT];
    snprintf(print_buffer, sizeof(print_buffer), "%c\n", single_char_input);
    printf("%s", print_buffer);
    snprintf(print_buffer, sizeof(print_buffer), "%s\n", row_input);
    printf("%s", print_buffer);
    snprintf(print_buffer, sizeof(print_buffer), "%s\n", sentence);
    printf("%s", print_buffer);
    return EXIT_SUCCESS;
}

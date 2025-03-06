# disclaimer, this is chat gpt output

.globl factorial
factorial:
    # Base case: if n == 0 or n == 1, return 1
    beqz $a0, base_case     # If n == 0, jump to base case
    li $t0, 1               # Load 1 into $t0 to check base case
    beq $a0, $t0, base_case # If n == 1, jump to base case

    # Recursive case: factorial(n) = n * factorial(n-1)
    addi $sp, $sp, -8        # Make space on stack
    sw $ra, 0($sp)           # Save return address
    sw $a0, 4($sp)           # Save n

    addi $a0, $a0, -1        # n - 1
    jal factorial             # Call factorial(n-1)

    # Restore registers
    lw $a0, 4($sp)           # Restore n
    lw $ra, 0($sp)           # Restore return address
    addi $sp, $sp, 8         # Clean up stack

    # Multiply result of factorial(n-1) by n
    mul $v0, $a0, $v0        # n * factorial(n-1)

    jr $ra                    # Return to caller

base_case:
    li $v0, 1                # If n == 0 or n == 1, return 1
    jr $ra                    # Return to caller

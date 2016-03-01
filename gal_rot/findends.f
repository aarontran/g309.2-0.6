        SUBROUTINE FINDENDS (ARR, NUM, MIN, MAX)
C       Given an array of numbers, this subroutine finds sensible
C       limits to display them with

        REAL ARR(50000), MIN, MAX

        INTEGER NUM, J

        MIN = 1E38
        MAX = -1E38

        DO 1000 J = 1, NUM
                IF (ARR(J) .GT. MAX) MAX = ARR(J)
                IF (ARR(J) .LT. MIN) MIN = ARR(J)
1000    ENDDO

        MIN = MIN - 0.1 * ABS(MIN)
        MAX = MAX + 0.1 * ABS(MAX)

        RETURN

        END



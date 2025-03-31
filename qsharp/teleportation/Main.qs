// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT license.
// Sourse: https://github.com/microsoft/QuantumKatas/blob/main/Teleportation/Tasks.qs

namespace Quantum.Kata.Teleportation {

    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Diagnostics;


    //////////////////////////////////////////////////////////////////
    // Welcome!
    //////////////////////////////////////////////////////////////////

    // "Teleportation" quantum kata is a series of exercises designed
    // to get you familiar with programming in Q#.
    // It covers the quantum teleportation protocol which allows you
    // to communicate a quantum state using only classical communication
    // and previously shared quantum entanglement.

    // Each task is wrapped in one operation preceded by the description of the task.
    // Each task (except tasks in which you have to write a test) has a unit test associated with it,
    // which initially fails. Your goal is to fill in the blank (marked with // ... comment)
    // with some Q# code to make the failing test pass.

    //////////////////////////////////////////////////////////////////
    // Part I. Standard Teleportation
    //////////////////////////////////////////////////////////////////

    // We split the teleportation protocol into several steps, following the description in
    // the Wikipedia article at https://en.wikipedia.org/wiki/Quantum_teleportation :
    // * Preparation (creating the entangled pair of qubits that are sent to Alice and Bob).
    // * Sending the message (Alice's task): Entangling the message qubit with Alice's qubit
    //   and extracting two classical bits to be sent to Bob.
    // * Reconstructing the message (Bob's task): Using the two classical bits Bob received from Alice
    //   to get Bob's qubit into the state in which the message qubit had been originally.
    // Finally, we compose these steps into the complete teleportation protocol.

    // Task 1.1. Entangled pair
    // Input: two qubits qAlice and qBob, each in |0⟩ state.
    // Goal: prepare a Bell state |Φ⁺⟩ = (|00⟩ + |11⟩) / sqrt(2) on these qubits.
    //
    // In the context of the quantum teleportation protocol, this is the preparation step:
    // qubits qAlice and qBob will be sent to Alice and Bob, respectively.
    operation Entangle(qAlice : Qubit, qBob : Qubit) : Unit {
        H(qAlice);
        CNOT(qAlice, qBob);
    }


    // Task 1.2. Send the message (Alice's task)
    // Entangle the message qubit with Alice's qubit
    // and extract two classical bits to be sent to Bob.
    // Inputs:
    //      1) Alice's part of the entangled pair of qubits qAlice.
    //      2) The message qubit qMessage.
    // Output:
    //      Two classical bits Alice will send to Bob via classical channel as a tuple of Bool values.
    //      The first bit in the tuple should hold the result of measurement of the message qubit,
    //      the second bit - the result of measurement of Alice's qubit.
    //      Represent measurement result 'One' as 'true' and 'Zero' as 'false'.
    // The state of the qubits in the end of the operation doesn't matter.
    operation SendMessage(qAlice : Qubit, qMessage : Qubit) : (Bool, Bool) {
        CNOT(qMessage, qAlice);
        H(qMessage);
        return (M(qMessage) == One, M(qAlice) == One);
    }


    // Task 1.3. Reconstruct the message (Bob's task)
    // Transform Bob's qubit into the required state using the two classical bits
    // received from Alice.
    // Inputs:
    //      1) Bob's part of the entangled pair of qubits qBob.
    //      2) The tuple of classical bits received from Alice,
    //         in the format used in task 1.2.
    // Goal: transform Bob's qubit qBob into the state in which the message qubit had been originally.
    operation ReconstructMessage(qBob : Qubit, (b1 : Bool, b2 : Bool)) : Unit {
        if (b1) {
            Z(qBob);
        }
        if (b2) {
            X(qBob);
        }
    }


    // Task 1.4. Standard teleportation protocol
    // Put together the steps implemented in tasks 1.1 - 1.3 to implement
    // the full teleportation protocol.
    // Inputs:
    //      1) The two qubits qAlice and qBob in |0⟩ state.
    //      2) The message qubit qMessage in the state |ψ⟩ to be teleported.
    // Goal: transform Bob's qubit qBob into the state |ψ⟩.
    // The state of the qubits qAlice and qMessage in the end of the operation doesn't matter.
    operation StandardTeleport(qAlice : Qubit, qBob : Qubit, qMessage : Qubit) : Unit {
        Entangle(qAlice, qBob);

        let (b1, b2) = SendMessage(qAlice, qMessage);
        ReconstructMessage(qBob, (b1, b2));
    }


    // Task 1.5. Prepare a state and send it as a message (Alice's task)
    // Given a Pauli basis along with a state 'true' as 'One' or 'false'
    // as 'Zero', prepare a message qubit, entangle it with Alice's qubit,
    // and extract two classical bits to be sent to Bob.
    // Inputs:
    //      1) Alice's part of the entangled pair of qubits qAlice.
    //      2) A PauliX, PauliY, or PauliZ basis in which the message
    //         qubit should be prepared
    //      3) A Bool indicating the eigenstate in which the message
    //         qubit should be prepared
    // Output:
    //      Two classical bits Alice will send to Bob via classical channel as a tuple of Bool values.
    //      The first bit in the tuple should hold the result of measurement of the message qubit,
    //      the second bit - the result of measurement of Alice's qubit.
    //      Represent measurement result 'One' as 'true' and 'Zero' as 'false'.
    // The state of the qubit qAlice in the end of the operation doesn't matter.
    operation PrepareAndSendMessage(qAlice : Qubit, basis : Pauli, state : Bool) : (Bool, Bool) {
        use qMessage = Qubit();
        if state == One {
            X(qMessage);
        }
        if basis != PauliZ {
            H(qMessage);
        }
        if basis == PauliY {
            S(qMessage);
        }
        let classicalBits = SendMessage(qAlice, qMessage);
        Reset(qMessage);
        return classicalBits;
    }


    // Task 1.6. Reconstruct and measure the message state (Bob's task)
    // Transform Bob's qubit into the required state using the two classical bits
    // received from Alice and measure it in the same basis in which she prepared the message.
    // Inputs:
    //      1) Bob's part of the entangled pair of qubits qBob.
    //      2) The tuple of classical bits received from Alice,
    //         in the format used in task 1.5.
    //      3) The PauliX, PauliY, or PauliZ basis in which the
    //         message qubit was originally prepared
    // Output:
    //      A Bool indicating the eigenstate in which the message qubit was prepared, 'One' as
    //      'True' and 'Zero' as 'False'.
    // To get the output, transform Bob's qubit qBob into the state
    // in which the message qubit was originally prepared, then measure it.
    // The state of the qubit qBob in the end of the operation doesn't matter.
    operation ReconstructAndMeasureMessage(qBob : Qubit, (b1 : Bool, b2 : Bool), basis : Pauli) : Bool {

        // 1. Reconstruct the state on Bob's qubit using the classical bits.
        ReconstructMessage(qBob, (b1, b2));

        // 2. Measure Bob's qubit in the same basis Alice prepared the original message in.
        let measurementResult = Measure([basis], [qBob]);

        // 3. Convert the Result to Bool and return.
        return ResultAsBool(measurementResult);
    }


    // Task 1.7. Testing standard quantum teleportation
    // Goal: Test that the StandardTeleport operation from task 1.4 is able
    // to successfully teleport the states |0⟩ and |1⟩, as well as superposition states such as
    // (|0⟩ + |1⟩) / sqrt(2),
    // (|0⟩ - |1⟩) / sqrt(2),
    // (|0⟩ + i|1⟩) / sqrt(2), and
    // (|0⟩ - i|1⟩) / sqrt(2)
    operation StandardTeleport_Test() : Unit {
        // Test teleportation for all 6 Pauli eigenstates.
        for basis in [PauliZ, PauliX, PauliY] {
            for state in [false, true] {
                // Allocate the qubits needed for entanglement.
                use (qAlice, qBob) = (Qubit(), Qubit());

                // Alice prepares the message, entangles, measures, gets bits.
                let (b1, b2) = PrepareAndSendMessage(qAlice, basis, state);

                // Bob receives bits, reconstructs, measures in the same basis.
                let receivedState = ReconstructAndMeasureMessage(qBob, (b1, b2), basis);

                // Verify that Bob measured the state Alice intended to send.
                // AssertBoolEqual(state, receivedState,
                //                 $"Teleportation failed for basis {basis} and state {state}.");

                // Reset qubits before next loop iteration.
                Reset(qAlice);
                Reset(qBob);
            }
        }
    }


    // Task 1.8. Entanglement swapping
    // Alice and Bob, independently from each other, each hold an entangled qubit pair in the
    // state |Φ⁺⟩ = (|00⟩ + |11⟩) / sqrt(2). They hand off one part of their pair to Charlie.
    //
    // Charlie can now teleport the state of Alice's qubit he holds onto Bob's remaining qubit,
    // thus teleporting the entanglement.
    // Just like in "standard" teleportation, Bob still needs to apply the reconstruction steps -
    // based on Charlie's measurement results - to the other qubit in his possession.
    //
    // After this procedure the state |Φ⁺⟩ = (|00⟩ + |11⟩) / sqrt(2) now spans across
    // Alice's and Bob's qubits which they didn't send to Charlie. They are now maximally entangled,
    // even though they never interacted in the first place!
    //
    // Outputs: A tuple of two operations.
    // The first operation is Charlie's part of the protocol.
    // It will take two qubits as input (the ones Alice and Bob sent to Charlie),
    // and produce a message, encoded as an integer, that will be sent to Bob.
    // The second operation is Bob's part of the protocol.
    // It will take the qubit that remained in Bob's possession and Charlie's integer as input,
    // and use the integer to adjust the state of Bob's qubit,
    // so that Alice's and Bob's qubits end up in the state |Φ⁺⟩.
    //
    // Note that you will likely need to create two separate helper operations that implement the two parts of the protocol,
    // and return them, rather than implement the solution in the body of this operation.
    //
    // Hint: You may find your answers for 1.2 and 1.3 useful, as similar steps are needed here.
    operation EntanglementSwapping() : ((Qubit, Qubit) => Int, (Qubit, Int) => Unit) {

        // Charlie's operation: Performs Bell measurement on his two qubits
        // and returns the outcome encoded as an integer (0, 1, 2, 3) indicating the correction needed.
        operation CharlieSwap(qA_Charlie : Qubit, qB_Charlie : Qubit) : Int {
            // Bell measurement circuit
            CNOT(qA_Charlie, qB_Charlie);
            H(qA_Charlie);

            let m1 = M(qA_Charlie);
            let m2 = M(qB_Charlie);

            // Map measurement outcome to required correction for Bob:
            // M=(0,0) -> measured |Phi+> -> Bob needs I -> return 0
            // M=(0,1) -> measured |Psi+> -> Bob needs X -> return 1
            // M=(1,0) -> measured |Phi-> -> Bob needs Z -> return 2
            // M=(1,1) -> measured |Psi-> -> Bob needs ZX -> return 3
            if (m1 == Zero and m2 == Zero) { return 0; } // I
            elif (m1 == Zero and m2 == One) { return 1; } // X
            elif (m1 == One and m2 == Zero) { return 2; } // Z
            else { return 3; } // ZX
        }

        // Bob's operation: Takes his remaining qubit and Charlie's integer result,
        // applies the necessary correction to achieve |Phi+> between Alice and Bob.
        operation BobSwap(qB_Bob : Qubit, charlieResult : Int) : Unit {
            if (charlieResult == 1) {
                // Need X correction
                X(qB_Bob);
            } elif (charlieResult == 2) {
                // Need Z correction
                Z(qB_Bob);
            } elif (charlieResult == 3) {
                // Need ZX correction
                Z(qB_Bob);
                X(qB_Bob);
            }
            // No action if charlieResult == 0 (Identity)
        }

        return (CharlieSwap, BobSwap);
    }


    //////////////////////////////////////////////////////////////////
    // Part II. Teleportation using different entangled pair
    //////////////////////////////////////////////////////////////////

    // In this section we will take a look at the changes in the reconstruction process (Bob's task)
    // if the qubits shared between Alice and Bob are entangled in a different state.
    // Alice's part of the protocol remains the same in all tasks.
    // As a reminder, the standard teleportation protocol requires shared qubits in state
    // |Φ⁺⟩ = (|00⟩ + |11⟩) / sqrt(2).

    // In each task, the inputs are
    //      1) Bob's part of the entangled pair of qubits qBob.
    //      2) the tuple of classical bits received from Alice,
    //         in the format used in task 1.2.
    // The goal is to transform Bob's qubit qBob into the state in which the message qubit had been originally.

    // Task 2.1. Reconstruct the message if the entangled qubits were in the state |Φ⁻⟩ = (|00⟩ - |11⟩) / sqrt(2).
    operation ReconstructMessage_PhiMinus(qBob : Qubit, (b1 : Bool, b2 : Bool)) : Unit {
        if not b1 {
            Z(qBob);
        }
        if b2 {
            X(qBob);
        }
    }


    // Task 2.2. Reconstruct the message if the entangled qubits were in the state |Ψ⁺⟩ = (|01⟩ + |10⟩) / sqrt(2).
    operation ReconstructMessage_PsiPlus(qBob : Qubit, (b1 : Bool, b2 : Bool)) : Unit {
        if (not b1 and not b2) {
            X(qBob);
        } elif (not b1 and b2) {
            // Identity - do nothing
        } elif (b1 and not b2) {
            Y(qBob);
        } else {
            // b1 and b2
            Z(qBob);
        }
    }


    // Task 2.3. Reconstruct the message if the entangled qubits were in the state |Ψ⁻⟩ = (|01⟩ - |10⟩) / sqrt(2).
    operation ReconstructMessage_PsiMinus(qBob : Qubit, (b1 : Bool, b2 : Bool)) : Unit {
        if not b1 {
            Z(qBob);
        }
        if not b2 {
            X(qBob);
        }
    }


    //////////////////////////////////////////////////////////////////
    // Part III. Principle of deferred measurement
    //////////////////////////////////////////////////////////////////

    // The principle of deferred measurement claims that measurements can be moved
    // from an intermediate stage of a quantum circuit to the end of the circuit.
    // If the measurement results are used to perform classically controlled operations,
    // they can be replaced by controlled quantum operations.

    // In this task we will apply this principle to the teleportation circuit.

    // Task 3.1. Measurement-free teleportation.
    // Inputs:
    //      1) The two qubits qAlice and qBob in |Φ⁺⟩ state.
    //      2) The message qubit qMessage in the state |ψ⟩ to be teleported.
    // Goal: transform Bob's qubit qBob into the state |ψ⟩ using no measurements.
    // At the end of the operation qubits qAlice and qMessage should not be entangled with qBob.
    operation MeasurementFreeTeleport(qAlice : Qubit, qBob : Qubit, qMessage : Qubit) : Unit {
        // 1. Entangle Alice's and Bob's qubits (assuming already done or done outside)
        // Entangle(qAlice, qBob); // Let's assume they are provided entangled in |Φ⁺⟩

        // 2. Alice interacts her message qubit with her entangled qubit.
        CNOT(qMessage, qAlice);
        H(qMessage);

        // 3. Apply the corrections using controlled operations instead of measurement.
        // Controlled-Z equivalent based on M (needs CNOT from M after H to B).
        CNOT(qMessage, qBob);
        // Controlled-X equivalent based on A (needs CNOT from A after CNOT(M,A) to B).
        CNOT(qAlice, qBob);
    }


    //////////////////////////////////////////////////////////////////
    // Part IV. Teleportation with three entangled qubits
    //////////////////////////////////////////////////////////////////

    // Quantum teleportation using entangled states other than Bell pairs is also feasible.
    // Here we look at just one of many possible schemes - in it a state is transferred from
    // Alice to a third participant Charlie, but this may only be accomplished if Charlie
    // has the trust of the second participant Bob.

    // Task 4.1*. Entangled trio
    // Input: three qubits qAlice, qBob, and qCharlie, each in |0⟩ state.
    // Goal: create an entangled state |Ψ³⟩ = (|000⟩ + |011⟩ + |101⟩ + |110⟩) / 2 on these qubits.
    //
    // In the context of the quantum teleportation protocol, this is the preparation step:
    // qubits qAlice, qBob, and qCharlie will be sent to Alice, Bob, and Charlie respectively.
    operation EntangleThreeQubits(qAlice : Qubit, qBob : Qubit, qCharlie : Qubit) : Unit {
        H(qAlice);
        H(qBob);
        CNOT(qAlice, qCharlie);
        CNOT(qBob, qCharlie);
    }


    // Task 4.2*. Reconstruct the message (Charlie's task)
    // Alice has a message qubit in the state |ψ⟩ to be teleported, she has entangled it with
    // her own qubit from |Ψ³⟩ in the same manner as task 1.2 and extracted two classical bits
    // in order to send them to Charlie. Bob has also measured his own qubit from |Ψ³⟩ and sent
    // Charlie the result.
    //
    // Transform Charlie's qubit into the required state using the two classical bits
    // received from Alice, and the one classical bit received from Bob.
    // Inputs:
    //      1) Charlie's part of the entangled trio of qubits qCharlie.
    //      2) The tuple of classical bits received from Alice,
    //         in the format used in task 1.2.
    //      3) A classical bit resulting from the measurement of Bob's qubit.
    // Goal: transform Charlie's qubit qCharlie into the state in which the message qubit had been originally.
    operation ReconstructMessageWhenThreeEntangledQubits(qCharlie : Qubit, (b1 : Bool, b2 : Bool), b3 : Bool) : Unit {
        if (not b3) {
            // Bob measured 0 (|0⟩ state), effective A-C state was |Φ⁺⟩
            if (b1) { Z(qCharlie); }
            if (b2) { X(qCharlie); }
        } else {
            // Bob measured 1 (|1⟩ state), effective A-C state was |Ψ⁺⟩
            if (not b1 and not b2) {
                X(qCharlie);
            } elif (not b1 and b2) {
                // Identity - do nothing
            } elif (b1 and not b2) {
                Y(qCharlie);
            } else {
                // b1 and b2
                Z(qCharlie);
            }
        }
    }
}

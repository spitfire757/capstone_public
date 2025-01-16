<?php
session_start();

// Database connection parameters
$servername = "localhost";
$username = "backend";
$password = "cobraSpitfire78!";
$dbname = "Capstone";

// Establish a connection to the database
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] === "POST" && isset($_POST['register'])) {
    // Get form inputs
    $email = trim($_POST['email']);
    $password = $_POST['password'];
    $confirm_password = $_POST['confirm_password'];
    $first_name = trim($_POST['first_name']);
    $last_name = trim($_POST['last_name']);
    $account_type = $_POST['account_type'];

    // Validate inputs
    if (empty($email) || empty($password) || empty($confirm_password) || empty($first_name) || empty($last_name)) {
        $message = "All fields are required.";
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $message = "Invalid email format.";
    } elseif ($password !== $confirm_password) {
        $message = "Passwords do not match.";
    } else {
        // Check if the email already exists
        $sql_check = "SELECT * FROM User WHERE Email = ?";
        $stmt_check = $conn->prepare($sql_check);
        $stmt_check->bind_param("s", $email);
        $stmt_check->execute();
        $result_check = $stmt_check->get_result();

        if ($result_check->num_rows > 0) {
            $message = "Email is already registered.";
        } else {
            // Hash the password
            $hashed_password = password_hash($password, PASSWORD_DEFAULT);

            // Insert the new user into the database
            $sql_insert = "INSERT INTO User (Email, Password, FName, LName, Account_Type) VALUES (?, ?, ?, ?, ?)";
            $stmt_insert = $conn->prepare($sql_insert);
            $stmt_insert->bind_param("sssss", $email, $hashed_password, $first_name, $last_name, $account_type);

            if ($stmt_insert->execute()) {
                // Redirect to the login page after successful registration
                header("Location: login.php");
                exit();
            } else {
                $message = "Error: " . $stmt_insert->error;
            }
        }
    }
}

// Close the database connection
$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <style>
        /* General Styles */
        * {
            margin: 0;
            padding: 0;
        }

        :root {
            --thunder-duration: 10s;
            --thunder-delay: 5s;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background-image: linear-gradient(to bottom, #030420, #000000 70%);
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            color: #c0c0c0;
            text-align: center;
        }

        /* Thunder and Rain Styles */
        hr.thunder {
            border: unset;
            position: absolute;
            width: 100vw;
            height: 100vh;
            animation-name: thunder;
            animation-duration: var(--thunder-duration);
            animation-timing-function: linear;
            animation-delay: var(--thunder-delay);
            animation-iteration-count: infinite;
        }

        hr:not(.thunder) {
            width: 50px;
            border-color: transparent;
            border-right-color: rgba(255, 255, 255, 0.7);
            border-right-width: 50px;
            position: absolute;
            bottom: 100%;
            transform-origin: 100% 50%;
            animation-name: rain;
            animation-duration: 1s;
            animation-timing-function: linear;
            animation-iteration-count: infinite;
        }

        @keyframes rain {
            from {
                transform: rotate(105deg) translateX(0);
            }
            to {
                transform: rotate(105deg) translateX(calc(100vh + 20px));
            }
        }

        @keyframes thunder {
            0% {
                background-color: transparent;
            }
            1% {
                background-color: white;
            }
            2% {
                background-color: rgba(255, 255, 255, 0.8);
            }
            8% {
                background-color: transparent;
            }
        }

        /* Register Form Styles */
        .register-container {
            position: relative;
            z-index: 100;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 30px;
            border-radius: 10px;
            width: 300px;
        }

        .register-container h1 {
            color: #61dafb;
            margin-bottom: 10px;
            margin-top: 13%;
        }

        .register-container form {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .register-container label {
            margin-bottom: 10px;
            font-size: 18px;
            display: block;
        }

        .register-container input[type="text"],
        .register-container input[type="password"],
        .register-container select,
        .register-container input[type="submit"] {
            padding: 10px;
            margin-bottom: 20px;
            width: 250px;
            border-radius: 5px;
            border: 1px solid #61dafb;
            background-color: #282c34;
            color: #c0c0c0;
            font-size: 16px;
        }

        .register-container input[type="submit"] {
            cursor: pointer;
            background-color: #61dafb;
            color: white;
            transition: background-color 0.3s;
        }

        .register-container input[type="submit"]:hover {
            background-color: #1e90ff;
        }

        .login-button {
            width: 75%;
            font-size: 14px;
            padding: 8px;
            margin-top: -10px;
            margin-bottom: 10px;
            background-color: #61dafb;
            border: 1px solid #61dafb;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        .login-button:hover {
            background-color: #1e90ff;
        }
    </style>
</head>
<body>

    <!-- Register Form -->
    <div class="register-container">
        <h1>Registration</h1>

        <?php if (isset($message)) { echo "<p>$message</p>"; } ?>

        <form action="register.php" method="post">
            <label for="email">Email:</label>
            <input type="text" id="email" name="email" required><br>

            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br>

            <label for="confirm_password">Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required><br>

            <label for="first_name">First Name:</label>
            <input type="text" id="first_name" name="first_name" required><br>

            <label for="last_name">Last Name:</label>
            <input type="text" id="last_name" name="last_name" required><br>

            <label for="account_type">Account Type:</label>
            <select id="account_type" name="account_type" required>
                <option value="user">User</option>
                <option value="admin">Admin</option>
            </select><br>

            <input type="submit" name="register" value="Register">
        </form>

        <!-- Login Button -->
        <a href="login.php">
            <button class="login-button">Login</button>
        </a>
    </div>

    <!-- Rain and Thunder Animation -->
    <script>
        let hrElement;
        let counter = 100; // Number of rain drops and thunder flashes
        for (let i = 0; i < counter; i++) {
            hrElement = document.createElement("HR");
            if (i == counter - 1) {
                hrElement.className = "thunder";
            } else {
                hrElement.style.left = Math.floor(Math.random() * window.innerWidth) + "px";
                hrElement.style.animationDuration = 0.2 + Math.random() * 0.3 + "s";
                hrElement.style.animationDelay = Math.random() * 5 + "s";
            }
            document.body.appendChild(hrElement);
        }

        console.log(
            "There are " +
            document.querySelectorAll("hr").length +
            " <hr> tags in this project :)"
        );
    </script>

</body>
</html>


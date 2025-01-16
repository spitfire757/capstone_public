<?php
session_start();

// Database connection parameters
$servername = "localhost";
$username = "backend";
$password = "cobraSpitfire78!";
$dbname = "Capstone";

// Establish a connection to the database
$conn = new mysqli($servername, $username, $password, $dbname);

// Check the connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $inputUsername = $_POST["username"];
    $inputPassword = $_POST["password"];

    // Prepare a SQL statement to select the user's hashed password from the database
    $sql = "SELECT * FROM User WHERE Email = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $inputUsername);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows == 1) {
        $row = $result->fetch_assoc();
        $hashedPasswordFromDB = $row["Password"];

        // Verify the input password against the hashed password from the database
        if (password_verify($inputPassword, $hashedPasswordFromDB)) {
            // Set the session variables for the signed-in user
            $_SESSION['User_ID'] = $row['User_ID']; // Correctly set the User_ID
            $_SESSION['Email'] = $row['Email']; // Correctly set the Email

            // Redirect to the home page
            header("Location: home_page.php");
            exit();
        } else {
            echo "Incorrect password.";
        }
    } else {
        echo "User not found.";
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
    <title>Login</title>
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
            background-image: linear-gradient(to bottom, #030420, #000000 70%);
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            font-family: 'Roboto', sans-serif;
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

        /* Login Form Styles */
        .login-container {
            position: absolute;
            z-index: 100;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 20px 30px;
            border-radius: 10px;
            text-align: center;
            color: #c0c0c0;
        }

        .login-container h1 {
            color: #61dafb;
            margin-bottom: 20px;
        }

        .login-container form {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .login-container label {
            margin-bottom: 10px;
            font-size: 18px;
            display: block;
        }

        .login-container input[type="text"],
        .login-container input[type="password"],
        .login-container input[type="submit"],
        .login-container .register-button,
        .login-container .login-button {
            padding: 10px;
            margin-bottom: 15px;
            width: 250px;
            border-radius: 5px;
            border: 1px solid #61dafb;
            background-color: #282c34;
            color: #c0c0c0;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        .login-container input[type="submit"],
        .login-container .login-button {
            background-color: #61dafb;
            color: white;
        }

        .login-container input[type="submit"]:hover,
        .login-container .login-button:hover {
            background-color: #1e90ff;
        }

        .login-container .register-button {
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

        .login-container .register-button:hover {
            background-color: #1e90ff;
        }
    </style>
</head>
<body>
    <!-- Login Form -->
    <div class="login-container">
        <h1>Login to SkySynth</h1>
        <form method="POST" action="">
            <label for="username">Email:</label>
            <input type="text" id="username" name="username" required>

            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>

            <input type="submit" class="login-button" value="Login">
        </form>

        <!-- Buttons -->
        <button class="register-button" onclick="location.href='register.php'">Register</button>
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

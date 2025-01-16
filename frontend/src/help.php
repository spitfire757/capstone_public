<?php
session_start();

// Check if the user is signed in by checking the session variable
if (isset($_SESSION['User_ID'])) {
    // User is signed in, get the user's email from the session
    $user_email = $_SESSION['Email']; // Adjust to match the correct session variable
} else {
    $user_email = null; // Set to null or empty string for display purposes
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resources</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #282c34;
            color: #c0c0c0;
            text-align: center;
            padding: 0;
            margin: 0;
        }

        h1 {
            color: #61dafb;
        }

        .top-bar {
            background-color: #1e90ff;
            color: white;
            padding: 10px 0;
            text-align: center;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
            display: flex;
            justify-content: center;
        }

        .top-bar a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            font-size: 16px;
        }

        .top-bar a:hover {
            background-color: #61dafb;
            border-radius: 5px;
        }

        .content {
            margin-top: 60px;
            padding: 20px;
        }

        p {
            color: #c0c0c0;
            font-size: 18px;
        }

        img {
            max-width: 80%;
            height: auto;
            margin: 20px 0;
        }

        iframe, embed {
            width: 80%;
            height: 600px;
            margin-top: 20px;
            border: none;
        }
    </style>
</head>
<body>

<!-- Top Bar -->
<div class="top-bar">
    <a href="home_page.php">Home</a>
    <a href="requests.php">Data Requests</a>
    <a href="settings.php">Account Settings</a>
    <a href="logout.php">Logout</a>
</div>

<!-- Content Section -->
<div class="content">
    <h1>Resources</h1>

    <?php if ($user_email): ?>
        <!-- Display user's email if signed in -->
        <p>Signed in as: <?php echo htmlspecialchars($user_email); ?></p>

        <!-- Display images -->
        <div>
            <img src="/test_heatmap.png" alt="Heatmap Image">
            <img src="/test_scatter3d.png" alt="3D Scatter Plot">
        </div>

        <!-- Display PDF below images -->
        <div>
            <embed src="/TEST.pdf" type="application/pdf" alt="CAPSTONE">
        </div>
    <?php else: ?>
        <!-- Prompt user to log in if not signed in -->
        <p>You are not signed in. Please <a href="login.php">log in</a> for personalized support.</p>
    <?php endif; ?>
</div>

</body>
</html>


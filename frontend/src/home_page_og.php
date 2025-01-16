<?php
session_start();

// Database connection parameters
$servername = "localhost";
$username = "backend";
$password = "cobraSpitfire78!";
$dbname = "Capstone";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check if the user is signed in by checking the session variable
if (isset($_SESSION['User_ID'])) {
    // User is signed in, get the user's email from the session
    $user_email = $_SESSION['Email']; // Adjust to match the correct session variable

    // Fetch User_ID based on the email
    $sql = "SELECT User_ID FROM User WHERE Email = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $user_email);
    $stmt->execute();
    $stmt->bind_result($user_id);
    $stmt->fetch();
    $stmt->close();

    // Fetch latitude and longitude for the user
    $sql = "SELECT l.Lat, lo.Lon
            FROM User_Lat l
            JOIN User_Lon lo ON l.User_ID = lo.User_ID
            WHERE l.User_ID = ?
            ORDER BY l.Lat
            LIMIT 1";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $user_id);
    $stmt->execute();
    $result = $stmt->get_result();
} else {
    $user_email = null; // Set to null or empty string for display purposes
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home Page</title>
    <style>
        /* Existing styles */
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #282c34; /* Dark background */
            color: #c0c0c0; /* Light grey text */
            text-align: center;
            padding: 0;
            margin: 0;
        }

        h1 {
            color: #61dafb; /* Robotic blue */
        }

        .top-bar {
            background-color: #1e90ff; /* Darker blue */
            color: white;
            padding: 10px 0;
            text-align: center;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
            display: flex;
            justify-content: center; /* Centers the links horizontally */
        }

        .top-bar a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            font-size: 16px;
        }

        .top-bar a:hover {
            background-color: #61dafb; /* Robotic blue */
            border-radius: 5px;
        }

        .content {
            margin-top: 60px; /* Space for the top bar */
            padding: 20px; /* Optional: Adds padding around the content */
        }

        input[type="submit"] {
            cursor: pointer;
            background-color: #61dafb; /* Robotic blue */
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        input[type="submit"]:hover {
            background-color: #1e90ff; /* Darker blue on hover */
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        table, th, td {
            border: 1px solid #c0c0c0;
        }

        th, td {
            padding: 10px;
            text-align: center;
        }

        th {
            background-color: #1e90ff; /* Darker blue */
            color: white;
        }

        tr:nth-child(even) {
            background-color: #333;
        }

        /* Hide table initially */
        #locationTable {
            display: none;
        }
    </style>
</head>
<body>

<div class="top-bar">
    <a href="requests.php">Data Requests</a>
    <a href="help.php">Resources</a>
    <a href="settings.php">Account Settings</a>
    <a href="logout.php">Logout</a>
</div>

<div class="content">
    <h1>Welcome to the Home Page!</h1>

    <?php if ($user_email): ?>
        <!-- Display user's email if signed in -->
        <p>Signed in as: <?php echo htmlspecialchars($user_email); ?></p>
        
        <!-- Form for latitude and longitude inputs -->
        <form method="POST" action="update_location.php">
            <label for="latitude">Enter Latitude:</label><br>
            <input type="number" name="latitude" id="latitude" required><br>

            <label for="longitude">Enter Longitude:</label><br>
            <input type="number" name="longitude" id="longitude" required><br>

            <input type="submit" value="Submit Latitude & Longitude">
        </form>

        <!-- Button to toggle table visibility -->
        <button onclick="toggleTable()">Toggle Location Data</button>

        <!-- Display latitude and longitude pairs as a table -->
        <?php if ($result->num_rows > 0): ?>
            <table id="locationTable">
                <thead>
                    <tr>
                        <th>Latitude</th>
                        <th>Longitude</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($row = $result->fetch_assoc()): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($row['Lat']); ?></td>
                            <td><?php echo htmlspecialchars($row['Lon']); ?></td>
                        </tr>
                    <?php endwhile; ?>
                </tbody>
            </table>
        <?php else: ?>
            <p>No location data found.</p>
        <?php endif; ?>

    <?php else: ?>
        <!-- Prompt user to log in if not signed in -->
        <p>You are not signed in. Please <a href="login.php">log in</a> to continue.</p>
    <?php endif; ?>
</div>

<script>
    function toggleTable() {
        var table = document.getElementById('locationTable');
        if (table.style.display === 'none') {
            table.style.display = 'table';
        } else {
            table.style.display = 'none';
        }
    }
</script>

</body>
</html>

<?php
// Close the connection
$conn->close();
?>


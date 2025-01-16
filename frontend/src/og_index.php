<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkySynth</title>
    <style>
        /* Background styles */
        .bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('/background.jpeg');
            background-position: center center;
            background-origin: content-box;
            background-size: cover;
            background-attachment: fixed;
            z-index: -2;
        }

        .lightning {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('/background.jpeg');
            background-position: center center;
            background-origin: content-box;
            background-size: cover;
            background-attachment: fixed;
            z-index: -1;
            transition: filter 1s ease-out; /* Smooth transition for brightness */
        }

        /* Flash effect */
        .flashit {
            -webkit-animation: flash ease-out 4s infinite;
            -moz-animation: flash ease-out 4s infinite;
            animation: flash ease-out 4s infinite;
        }

        @-webkit-keyframes flash {
            from { opacity: 0; } 
            92% { opacity: 0; }
            93% { opacity: 0.6; }
            94% { opacity: 0.2; }
            96% { opacity: 0.9; } 
            to { opacity: 0; }
        }

        @keyframes flash {
            from { opacity: 0; } 
            92% { opacity: 0; }
            93% { opacity: 0.6; }
            94% { opacity: 0.2; }
            96% { opacity: 1; } 
            to { opacity: 0; }
        }

        /* Container and button styles */
        body {
            font-family: 'Roboto', sans-serif;
            color: #c0c0c0;
            text-align: center;
            margin: 0;
        }

        h1 {
            color: #61dafb;
            font-size: 4rem;
            margin: 0;
            padding-top: 50px;
            text-shadow: 0 0 10px rgba(0, 0, 0, 0.7);
        }

        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            z-index: 1;
            position: relative;
        }

        .content {
            width: 300px;
        }

        .btn {
            display: block;
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            font-size: 18px;
            border-radius: 5px;
            border: 1px solid #61dafb;
            background-color: rgba(40, 44, 52, 0.9);
            color: #c0c0c0;
            text-decoration: none;
            transition: background-color 0.3s, color 0.3s;
        }

        .btn:hover {
            background-color: #1e90ff;
            color: #ffffff;
        }
    </style>
</head>
<body>
    <!-- Background layers -->
    <div class="bg"></div>
    <div class="lightning"></div> <!-- No 'flashit' class initially -->

    <!-- Main content -->
    <div class="container">
        <div class="content">
            <h1>SkySynth</h1>
            <a href="/login.php" class="btn">Login</a>
            <a href="/register.php" class="btn">Register</a>
        </div>
    </div>

    <script>
        // Gradually increase the brightness and start the flash effect after 2 seconds
        window.onload = function() {
            // Wait for 2 seconds before applying the brightness and starting the flash effect
            setTimeout(function() {
                const lightningElement = document.querySelector('.lightning');
                lightningElement.style.filter = 'brightness(3)'; // Apply high brightness
                lightningElement.classList.add('flashit'); // Start the flash effect
            }, 1000);
        };
    </script>
</body>
</html>

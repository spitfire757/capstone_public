<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkySynth</title>
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

        /* Main Content Styles */
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
            position: relative;
            z-index: 1;
        }

        .content {
            width: 300px;
            z-index: 2;
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
    <!-- Thunder and Rain Animation -->
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

    <!-- Main content -->
    <div class="container">
        <div class="content">
            <h1>SkySynth</h1>
            <a href="/login.php" class="btn">Login</a>
            <a href="/register.php" class="btn">Register</a>
        </div>
    </div>
</body>
</html>


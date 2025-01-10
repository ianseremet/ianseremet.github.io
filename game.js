const boat = document.getElementById("boat");
const gameContainer = document.getElementById("gameContainer");
let isJumping = false;
let gameStarted = false;
let rockInterval;

const startMessage = document.createElement("div");
startMessage.id = "startMessage";
startMessage.innerText = "Press Up Arrow to Start";
startMessage.style.cssText = `
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 24px;
    color: white;
    background-color: rgba(0, 0, 0, 0.7);
    padding: 10px 20px;
    border-radius: 10px;
    text-align: center;
`;
gameContainer.appendChild(startMessage);

document.addEventListener("keydown", function (event) {
    if (!gameStarted && event.code === "ArrowUp") {
        startMessage.style.display = "none"; 
        startGame();
    }
});

function startGame() {
    gameStarted = true;
    spawnRocks();
}

function jump() {
    if (isJumping) return;
    isJumping = true;
    let jumpHeight = 0;

    const jumpUp = setInterval(() => {
        boat.style.bottom = (parseInt(boat.style.bottom) || 0) + 5 + "px";
        jumpHeight += 5;

        if (jumpHeight >= 100) {
            clearInterval(jumpUp);

            const jumpDown = setInterval(() => {
                boat.style.bottom = (parseInt(boat.style.bottom) || 0) - 5 + "px";
                jumpHeight -= 5;

                if (jumpHeight <= 0) {
                    clearInterval(jumpDown);
                    isJumping = false;
                }
            }, 20);
        }
    }, 20);
}

document.addEventListener("keydown", function (event) {
    if (event.code === "ArrowUp" && gameStarted) {
        jump();
    }
});

function spawnRocks() {
    rockInterval = setInterval(() => {
        const rock = document.createElement("div");
        rock.classList.add("rock");
        gameContainer.appendChild(rock);

        rock.style.left = "800px";

        const moveRock = setInterval(() => {
            const rockLeft = parseInt(window.getComputedStyle(rock).getPropertyValue("left"));
            const boatBottom = parseInt(window.getComputedStyle(boat).getPropertyValue("bottom"));

            rock.style.left = rockLeft - 5 + "px"; 

            if (rockLeft < 50 && rockLeft > 0 && boatBottom <= 50) {
                clearInterval(rockInterval);
                clearInterval(moveRock);
                rock.remove();
                alert("Game Over! Restarting...");
                location.reload();
            }

            if (rockLeft <= -50) {
                rock.remove();
                clearInterval(moveRock);
            }
        }, 20);
    }, 2000); 
}

# 4-Square Tournament

A simple scorer for keeping a 4-square tournament moving. Add your players,
record each round, and let the app track scores and the queue.

## Download

From the project's GitHub page, open **Releases** and download the ZIP for your
computer:

- **Windows:** `FourSquare-windows-x64.zip`
- **Mac with Apple silicon:** `FourSquare-macos-arm64.zip`
- **Mac with an Intel processor:** `FourSquare-macos-x64.zip`

Unzip the download, then open `FourSquareTournament.exe` on Windows or
`FourSquareTournament.app` on Mac. No Python installation is needed.

The app is not signed, so your computer may show a first-launch warning. On
Mac, Control-click the app, choose **Open**, and confirm. On Windows, only
proceed past SmartScreen if you downloaded the app from this project's GitHub
Releases page.

## Publishing a release

Pushing a version tag such as `v1.0.0` starts a GitHub Actions build for Windows,
Apple silicon Macs, and Intel Macs. When all three builds finish, GitHub creates
a release for that tag and attaches the downloadable ZIP files. Find the
downloads on the repository's **Releases** page. To publish a version from the
repository, run:

```sh
git tag v1.0.0
git push origin v1.0.0
```

## Quick start

1. Add at least four players in starting order: King, Queen, Jack, First
   Square, then anyone waiting in the queue.
2. When a round ends, click **Eliminate from square** for the player who is out.
3. Record an elimination point or penalty if needed, then choose **Record
   round**. The remaining square players earn their position points, and the
   eliminated player moves to the end of the queue.

## During the tournament

- **Click** a square's button to record an elimination, or press **4**, **3**,
  **2**, or **1** for King, Queen, Jack, or First Square.
- In the round dialog, the number keys select a player by their board or queue
  number. **Tab** changes fields; **Enter** records the round.
- **Edit game state** corrects scores or reorders players. **Undo last change**
  reverses the most recent round or correction.
- The tournament log records rounds and manual corrections. Choose **Save
  log...** to save a text copy.
- **Standings** shows the current score ranking. **R** resets the tournament;
  **X** closes the app.

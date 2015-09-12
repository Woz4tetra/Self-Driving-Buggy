
/* To add a new sound effect:
			1. Convert to RSO
			2. Put in NXT System Files (C:\Program Files (x86)\Robomatter Inc\ROBOTC Development Environment\NXT System Files)
			3. Put PlaySoundFile("yourFile.rso"); in your code to download

			** The NXT has a capacity of ~100 kB and the RSO converter caps at 64kb per file
					- RobotC won't tell you if you've run out of space when you try to load a sound file
					- RobotC WILL tell you if you've run out of space when you try to load a program
			** Any files deleted in the program must be deleted manually on the NXT, to be safe, you can delete all custom sound files first
			** Stay under 16 characters for file names
			** For the WAV to RSO converter:
					- select "linear" and "compressed"
					- set bit rate to 0...16000
						- 8000 is recommended - gets ok quality with small sile sizes
						- 16000 is ok for small sound bits
*/

//void coinTest()
//{
//	/* For fade out at last run through: */
//	for (int counter = 0; counter < 5; counter++)
//	{
//		ClearSounds();
//		PlaySoundFile("Coin.rso");
//		wait1Msec(500);
//	}
//	PlaySoundFile("1up.rso");
//	while(bSoundActive) { }
//	wait1Msec(100);
//}

//void accerlativeCoinTest()
//{
//	/* No fade out + acceleration: */
//	for (int counter = 0; counter < 20; counter++)
//	{
//		PlaySoundFile("Coin.rso");
//		wait1Msec(75 + counter * 10);
//		ClearSounds();
//	}
//	PlaySoundFile("1up.rso");
//	while(bSoundActive) { }
//	wait1Msec(100);
//}

//void infiniteTest()
//{
//	while (true)
//	{
//		PlaySoundFile("Waka.rso");
//		while(bSoundActive) { }
//	}
//}

void recommendedFilesTest()
{

	PlaySoundFile("Coin.rso"); // 6.96 kB
	while(bSoundActive) { }
	wait1Msec(100);

	//PlaySoundFile("SMB3 Fortress.rso"); // 32.9 kB
	//while(bSoundActive) { }
	//wait1Msec(100);

	//PlaySoundFile("SM64StageClear.rso"); //13.6 kB
	//while(bSoundActive) { }
	//wait1Msec(100);

	//PlaySoundFile("FFIIVictory.rso"); // 18 kB
	//while(bSoundActive) { }
	//wait1Msec(100);

	PlaySoundFile("ZeldaSecret.rso"); // 8 kB
	while(bSoundActive) { }
	wait1Msec(100);
}

void toneTest()
{
	PlayTone(523.25, 10);
	while(bSoundActive) { }
	wait1Msec(50);

	PlayTone(523.25, 500);
	wait1Msec(500);

	ClearSounds();
	wait1Msec(500);
}

task main()
{
	toneTest();
	//coinTest();
	//accerlativeCoinTest();
	recommendedFilesTest();
	//infiniteTest();

	PlaySoundFile("StarPower.rso");
	while(bSoundActive) { }
	wait1Msec(100);

	while(true)
	{
		PlaySoundFile("SMB2overworld.rso"); // 44 kB
		while(bSoundActive) { }
		wait1Msec(100);
	}

	//PlaySoundFile("1up.rso"); // 6.34 kB
	//while(bSoundActive) { }
	//wait1Msec(100);

	//PlaySoundFile("SMB OuttaTime.rso"); // 11.6 kB
	//while(bSoundActive) { }
	//wait1Msec(100);

	//PlaySoundFile("SMB3YoureDead.rso"); // 12.6 kB
	//while(bSoundActive) { }
	//wait1Msec(100);

	//PlaySoundFile("MegaManXStage.rso"); // 27.7 kB
	//while(bSoundActive) { }
	//wait1Msec(100);

	//PlaySoundFile("DrWilysCastle.rso");
	//while(bSoundActive) { }
	//wait1Msec(100);

	//PlaySoundFile("MegaMan2Stage.rso");
	//while(bSoundActive) { }
	//wait1Msec(100);

	//PlaySoundFile("! Attention.rso");
	//while(bSoundActive) { }
	//wait1Msec(100);
}

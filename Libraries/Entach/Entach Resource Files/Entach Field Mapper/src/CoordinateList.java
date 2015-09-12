
import java.awt.Color;
import java.awt.Graphics;
import java.util.ArrayList;

public class CoordinateList
{
	private ArrayList<Coordinate> coordinateList = new ArrayList<Coordinate>();
	
	public CoordinateList()
	{
		
	}
	
	public void addCoordinate(Coordinate newCoordinate)
	{
		coordinateList.add(newCoordinate);
	}
	
	public void removeCoordinate(int index)
	{
		coordinateList.remove(index);
	}
	
	public Coordinate getCoordinate(int index)
	{
		return coordinateList.get(index);
	}
	
	public int getListSize()
	{
		return coordinateList.size();
	}
	
	public void redrawPath(Graphics g)
	{
		if (coordinateList.size() >= 1)
			for (int index = 0; index < coordinateList.size() - 1; index++)
				g.drawLine((int)this.getCoordinate(index).getX(), (int)this.getCoordinate(index).getY(), (int)this.getCoordinate(index + 1).getX(), (int) this.getCoordinate(index + 1).getY());
	}
	
	public void printContent(Graphics g, int fieldImageHeight)
	{
		g.setColor(new Color (0, 0, 0));
		
		g.drawString("Index",540,20);
		g.drawString("X (cm)",600,20);
		g.drawString("Y (cm)",660,20);
		for (int index = 0; index < coordinateList.size(); index++)
		{
			double xCoordinate = coordinateList.get(index).convertCoordinate(coordinateList.get(index).getX() * 1000); // the "* 1000" is for rounding 
			double yCoordinate = coordinateList.get(index).convertCoordinate((fieldImageHeight - coordinateList.get(index).getY()) * 1000);
			
			xCoordinate = Math.round(xCoordinate);
			yCoordinate = Math.round(yCoordinate);
			
			xCoordinate /= 1000;
			yCoordinate /= 1000;
			
			g.drawString("" + index,540, 20 + (index + 1) * 15);
			g.drawString("" + xCoordinate,600,20 + (index + 1) * 15);
			g.drawString("" + yCoordinate,660,20 + (index + 1) * 15);
		}
	}
	
	public void removeAllCoordinates()
	{
		for (int index = 0; index < coordinateList.size(); index++)
		{
			coordinateList.remove(index);
			index--;
		}
	}

	public ArrayList<Coordinate> getArrayList()
	{
		return coordinateList;
	}
	
	public void drawGhostPath(Graphics g, double xCoord, double yCoord, boolean shiftPressed)
	{
		g.setColor(new Color (176, 176, 176));
		Coordinate correctedCoordinate = new Coordinate(0, 0);
		
		if (coordinateList.size() >= 1 && xCoord > 0 && xCoord < 432 && yCoord > 0 && yCoord < 432)
		{
			if (shiftPressed == true)
			{
				correctedCoordinate = correctedCoordinate.getAngleCorrectedCoordinate(coordinateList.get(coordinateList.size() - 1), xCoord, yCoord);
				g.drawLine((int)coordinateList.get(coordinateList.size() - 1).getX(), (int)coordinateList.get(coordinateList.size() - 1).getY(), (int)correctedCoordinate.getX(), (int)correctedCoordinate.getY());
			}
			else
				g.drawLine((int)coordinateList.get(coordinateList.size() - 1).getX(), (int)coordinateList.get(coordinateList.size() - 1).getY(), (int)xCoord, (int)yCoord);
		}
	}
}

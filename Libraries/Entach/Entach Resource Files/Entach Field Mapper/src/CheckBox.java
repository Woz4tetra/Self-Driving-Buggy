
import java.awt.*;

import javax.swing.*;

public class CheckBox
{
	Point startPoint;
	Point endPoint;
	boolean isAcceptingClicks = true;
	
	JCheckBox checkBox = new JCheckBox();
	
	public CheckBox(Point start, Point end, JPanel panel)
	{
		startPoint = start;
		endPoint = end;
		
		checkBox.setBounds(startPoint.x, startPoint.y, endPoint.x - startPoint.x, endPoint.y - startPoint.y);
		checkBox.setSelected(true);
		panel.add(checkBox);
	}
	
	public void setIsChecked (boolean checked) {
		checkBox.setSelected(checked);
	}
	
	public boolean getIsChecked() {
		return checkBox.isSelected();
	}
	
	public void toggleIsChecked() {
		checkBox.setSelected(!checkBox.isSelected());
	}
		
	public boolean isPointInsideCheckBox (Point mousePoint)
	{
		if (mousePoint.x > startPoint.x && mousePoint.y > startPoint.y && mousePoint.x < endPoint.x && mousePoint.y < endPoint.y)
			return true;
		else
			return false;
	}
	
	public void removeCheckBox(JPanel panel) {
		panel.remove(checkBox);
	}
}

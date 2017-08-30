#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private slots:
    void on_enableButton_clicked();

    void on_disableButton_clicked();

    void on_disabletempButton_clicked();

private:
    Ui::MainWindow *ui;
    int getScutumStatus();
};

#endif // MAINWINDOW_H

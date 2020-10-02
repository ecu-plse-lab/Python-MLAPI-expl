#!/usr/bin/env python
# coding: utf-8

# ## Introduction

# This short notebook compares the accuracy of four classification models over a numeric set of data:
# - Decission Trees
# - Random Forest
# - Support Vector Machine
# - K Nearest Neighbors
# 
# The data set used is a cleaned up version of cardio_train.csv available at 
# https://www.kaggle.com/sulianova/cardiovascular-disease-dataset
# where a number of explicative features are used to predict the presence ("1") or absence ("0") of a cardiovascular disease (CARDIO_DISEASE).
# 
# An insightful graphical representation of the decision tree is also included.
# 
# Enjoy reading!
# 

# ## Data analysis and clean up

# I have done a bit of pre-processing with Excel before uploading the csv file into colab. Excel is still pretty convenient for correcting wrong data manually, as shown in the image below.
# Also, there were quite a few outliers (AP_HIGH or AP_LOW) which have been removed.

# ![image.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA/0AAAB3CAIAAADenrcUAABObElEQVR4nO2deUBM6/vAz5mlaSrtKinaN1lSlywlSxRaKBVChSxFLsmSrj03VEq4lrL1JWu2QkS2i6TruggpUihL+zI1y/lNGy1nppmaac6c3/v5a+aZc973ed5nOc85c+YMCUEQCAAAAAAAAAAAAOAakqgVAAAAAAAAAAAAAEIH9P0AAAAAAAAAAAD+AX0/AAAAAAAAAACAf5r7fubb7SPMb3hnpyxQg+tSfPvYxxWTSQQYJkkqaQ0a7eq/NtDFWKabdaM/Wfub3V+1M89nRttQW8ir35wL27gr4da/ecW1ZIW+A0dPD9yyxllPEoIaND/0HSa02JpkvPrBP1vMeT3B6dTgLPZHE08abE+/tdy4cSLWx+jRAx4sLTrlcIfjYnYwYONeDVKYLKc1dOqKHWFzzWRh3uxgD953FvNwfqydRPNyPlhuZPdp+/dGldDnhVuEQYergT5+jsNxHa8rtIZFYLFgAqF+IFh25vkvRx0oHarNzN4xctDZKf/8HWRAbDAjbYn+hBSPuy/DhjYsLOPf9eYjHy5+seLp0IkYNeEXaAFc18qzRGl1M8ffd4b7Wypy8CsXPzrnddnS76dc+DFISBY1UZV15s+Nu07dev6xjCmlZjTCeeG6kHlDlRHeQuLN9QXqPOYGe6G2rY9gL9THUpa0er9RbgGbQmb270Hnvkoc1CNwsIhrLarNvbA5KPTE/fcVTBZCVuk/0W/bdj9LxfJ4597ogXeQsqSTtYJPtfmDn5BjU3vWTWm1ZkpW+HByk4T53yaLYQ/93yfP7Qlz8gt3KyBOiwkL4nDQweCHewan/7PJ7OdoZYmeeq5nTCKzby/tQ+Bj8ZEft4ImzLo3/kTy1lGKdAGozTFV0T3eqZXvoKoIJ/C4VBuO+nwNK3YZ8qfmsYy/7BQaSwRSen2Rxay8oMdXfLWJHF3MbH8o4bRK/C44P17jOHWfi1M4lIs4w6hGzeczDtiZ7v4t9Z+t5uSfgzEyQ8xGP/Z7cW1+zc4mA6n/Q6885x6N/Gsk56Xj03mdWkBOxY3OuU1t6zhu1QMFLg1w65G7UHnQHS3UUtYSDjvBynMuNQQrsyL/adLeNUtHpLy6fiPkN+nOzNFJqtPiLvQN2UTZF3e9zMZZrkla9yraadTWWq+oE5kOg9TIlR8zzoct8R77Hsk4OqVng+beVzp9JOvs4HUQRFDrmb992UHn5EU6bbOB02KSuQ74cy82rMr31ze6e7j+YfBqlzVfjRoHOM3LbKVEB6uBjpznhUrP+he1l2ap+csn5uy2IXPcuB1E7QkT9DalpBYGGvRmxzjjecptumLl7dS3zKEm7HVl5aXezBnoYqsKP8WsCT9BD+CWnkVqvzyImD116hL1/+JdlHjsWtHpnKV8IkSLav8Lnzx6JzQ/KuHZpIFqpJLXNw+sWjx+9JsL93da8RQSajxORn+9x9l6feWMqJPPppipIIXPLkX+HjDGteLv5LmdU2+0HKedOIbo66iZ3tdGJNw5Pl6TCtcV3d8xY4rL731eHnHkGHh1KZ2qFVBn1OYVwYYcZ78s6vOKixUsjospD3XxcMDNU/WDE3r1Kks49jDYzKqxJiPfr8Q/kOwl3RSJvMYMUvb3Rsc5t22OXWM3/Y37dlFtiHOqotDZlec2ZqfyhUc4VRuOOxC0fGI2nbVctt49PXqMLFtQcXfjsvO6Gx/OZXeu3F3M0yrp1x/x+VhwzqAPwnlqTuWC+bbZ9N7T5tuFBB2+v858dHN7SXtw5ESR3TY3DQKU3Twx50Me05Tj0vFHZxeQU3Gz5NxZSbacl2socjpo8DIy98jhnsKoxnZlQD7p6GSB2ENziMe2i72qzR3XHJ2TsrgPp3MkQYP8uHzo5oCZW2dLPY8+mFjo5NVwXEdKLm3e8mLcnufbp/VscJmc1nDvPam2+Yhqzy61TVBXByf28dpinbhqefzk83M0OSxSm8Wcx7NmBBnt8T5TDPalvvyBWPN6VbOLCHWpOUMytpugvislrXThTEWY+e7mbcbUhXZJqbc+rzbRJCBfb6X8Z2h3oC/hE4ZNaJocNYBbA1N6jfz998mRPtcy6C4TupDR3WKpEC1Cvp4OCX3ncOR5qEPjZSVlk0lrT50strBdu9/3/u88hQRvE5Ve2rTxmVXU88iZjdr3tpi+/WzvgddhSUZn1QvS5tXMJpi5r3NkLUNt2MWd/U5CdeTq00/cGSq8fpXHnRa1gmWUKki1WyPYkOPiF3oHiy/MxeTuKYL6BDti4tFbW6zs6y+Isb4kxmcOtR18I7fBIh5jpvLpzqnTL1ocvLZ9rHK3pmrzpp1fec7TCzZfONK62nDZkKgzP+aPsyMCtrg/2j4CfhS69ITG+ge+uvXtJm/JyL1uEPlZcM5w6Hk6mLqDJVKcNM915azDKaGjnWQbJBU3Dp9juByZXP+FBg9KcVk6vmwTyAK2bIQsWyrZurNa0GJe7qFo2JEdnEfuQhnnYKxQjwut4e1LApnh7pN72t/6u2pxnx6C1wENVsGZuH9GL49TlCV6TQwKOZk7+3dd9pGd/s+te3SbqImtjiwEeY2+gpizS4MjTAnz1bumDZ8VdNbuhJsqly1/LuY8RV41Y1XmJO07na3nZKnSPU0/JOSl5gLZzN5W7sj1+9UzHalfbt3MH7p03rjCvxJul/jNViq/c+NJ7/Gb2cnKU98vKhPq4RDAaFuyIBKli7+z6Q5LhWlRXfrN++QJ8eMVWuovNWT6lL5/pd79vnI2LyHBE/TMW3fpY3Y5tTyqEFStZ82uVyKrk+rx28eQLV2mkKfPdSQt9XEcM3KoaW9pJS09PsfgSItaQRes2q0RbMhx8UvtFa5WGAhzMTvwFKzl4qE792hyid00BZiVd+Z/2ROWTy+5llP/GU8xU/3fHneXo/oxNyLtVAV4RY33VO3KynOOHwHnC3d4qzZE/YV7gs9ZLfnTMYa8/LBy8N0Feo0lg7dk5FY3IP4WnLMhHHoe7lN3iNSouTOVxsdd+Oo4m909IN8vHb4iP/OajRTPenFcOn4QzAJyb4R+dlYLBv+UdRCKhqo8NVRoI3e+jHMyVqjHhdbweHQmKKsoMZ8Vl7OgHt1ywZ/5+vjhAqddo+svowz3ci33OfZ8ycZBJIhV8qNMVlW56TpibfJC47kXquv/gIA8KPh20pI+9d+1HnWU/d8vJcm/bc1MW6HPS6B2efAe1usj7C0Wr0kaGzuRyzw/F1OR24DIj3hXlXP1/mHRq2kyplMWHDm3xoyfbgopPjmjT9Kva670iu+syU0fdbxKPKwG5/G7AmWo/Rji4uvptQ4D0268sJg6Qm3U5/6BN+5VzZ7wd8p9WVu/gSSsm8A5gNtQV3g/Yley9KTjv3G5NM6Dkt1gqSAtamdh9Y9immJ/5TZZSlBW7QmVFpeyeAwJHmCVfGcvVE9O98qhr1JH6nE0i0OIwoqT9j6+c/bAodN7l/zpk0PXGOHsG7wpYExvrlbwXSuI1c87pTZvdBxy/I3GyS8dLT5syG0xu3A4qKcjTxE1p80evP3ohSJX755vEk4WOYbbSEfzpHb9JpU3Aj1us2h0ie/V7PctD6xdU5vHVG2k8ysPCTpf+KdVtanjXuVIhov3rj5vNdEeHrzh3iKD5uXgLRm51w2+FpwTnHseriWrY8iDvL2Nfjt8Ks9ziRZUcOZImqF3mBlfN65yWDp+6PwCcmqE6toP86tNbabDUFTlLafaj9xR5HBOYY7GdnbATsCjC5mfCwrJKqry3XSXT+3juCPPcgvtVQ42vGXV1ijH3V8TbSNJVOwpX/alsIZtNVtOGRv26NkGFlKXsmRwTFXj9/Qt7wbjk64PDstP2LJjhMWK9akjVsIcTyRbLCaXAWElz7MNHyHFl7zNFtdN83fS5S/3YXnnPekRo5sHZzzZMHJGCcSTIRBPq8F5/C4hNXKiddX6lOfllTfSTcZFKRBVbcZobr+RXtnzxh147O4hEu3uacacCRwDuP7dr0IGwdRe5lP+vBA2XpbLYDwoKXxLBWpROwupSkqS378U0VsXJNa3wm+QUk9FAi8hwRsEBWW50s9fqiEI9Q5c9FXqUL08DmZxDlGikpn7mj3ua9gL++3l7eMb/J0mVdzN2MDtvJ7/WoF0Tm3e6DjkUI2AWUjLYyfCYjIhmEDg7JcOF5/zYkJdOhw028l5cDYEFac5o4JjTufNGHniFM318FBKLo9q59Xfdz7v7BW/qrCxTi6rtG7vHP3rmmSX1Oaaqu3owsrnCThfeIRLteFe5cjGi1ZM3DqXsHKRUau2l5OLW16a5lY3+FtwDnAcpIOSxQNE3ZnzRoTGxGctXkM8cTRzmO8xvi/Yc1o6nun8AvLRCLVvU3moHjzBoQHuTOXhaqxQS1kLeOr7kZIb8ZcqR20Zyft3Q12i4uahM8qb/81qeoAHxMqLHmsVd32zjZOc+fgxVJ/4c5+medf/xo8ip6LKDqNaeUlB3P5CFsDgcE+nP7fGD/19q/UcDqnVYjH/5W1IxcmbQvabr15/03avLccfoqBBoCqoqan9fLiBohQR4r3V42E1ujQ+F2RtJg4rPHT7cs1j9TFB7MmJemNsqAtSL6rcrRi1diS14wFEbQKXAIZaFDJe6VhJoVsqYIvaQrEcP4q5Iv7Kt4nTft03UpNx5mL+4Pmj6n8eLKiQkDAfO4oy90hCntuCn78IQL4l/bHutV2YP8RplTpUjy+YX9IvPIKsnYc0jEXp2c8uYP2c45YP/ylFzLp4i3frWiFYtdvQmWpJUFPvWZz7oRwZ2TQ7Uvnm9Se5Pho9KJz98udsblawuCwmP6eeqHDz1M9O027OxMDNJ069PyflcX4ACWrq+3mIGVhKf7CxrJzExjM7XlnNmKl/+8JCIwEc1bmnaju4ZAT3lW+QdEe+tIVbtemgyhElyCQSkdyie+PmYoVfm3GrG/NL+VpwdLj1PJynXj5CnpfVhNWmzpsYvDb+8Xjy/z7ab3Tp1QkXtF86vhDAAnbUCLXorMp+CgUSiqgj81Ac0ODsaBlhlrI2dNT3M6s/P7scHbjsos662+683QvVVZCvFw5d0Zi65tdPRwiaTlN0t8ReKHKcozrpjy3DrVY4LmZFrZlmqSlV8+nZ9aOhwZd6jHBV6vKXEbKCGJzQe0b4H/8bFnyQwhrU5qPOLiahz5w/fz84cvm22Y//HNZN514CWo1OASuNtTf7/cCuMthmf0N2kAaOtSpZuetCwbDlo/h5mqxoTOAawArc9uw8wrVU6BbByq4b1x20Wey8gh4V6GSmRi59eyturd9BasDleQ23PgosJOQcQtYPsQ5ynAftXuc+tDeh6J/E7UtXXOobNV8Wft1J9VC+ceZK5aMYn/DjH47HLLDSkIIZJS/PxZx+b+zxm4IA6murWiFYtdvQiZAjD5ntrT9609JDBjs9LVSRL4+PrVyXou1701oConD0i1zP37hZkc15MXn52SJ3uHjq5+DSNrOnBMxYd9Eg6DY7MunNYt5jhqQ95/D/Xto4u/yulRZj18Xf4fOfqpwzooOV5xw/As4XocJjMnJcpXm0izu7XBu59zxcShavVsrZzZ8WNG9DCKnGda99l5/k1RkEsYCtilvL1rVtZ/WrO+/wyNIBnEfmqTi0hZujPTszYCfh0Pf/vJcIlpDTHDDGI+pO0DQTwXzD0BGsDwmHbulP3dnyF+PstZna74/Yk+9nLdPRnXv6nsrODTvnDQl4X8Kk9tQZNMppbeoBTwtluOEOv++HJ0sdbTmgxMjwV7cCtHjpfoidHFy91SgELZ9dq078tvzToMb3nBaT5wHZB8z+ATt8jk7+PWrm3TX9BeAHTvNqthR1tBrCg9DL1s5w2eoPc7Y23YdIGTrOMu/gxd/mjf35VHjMmsA9gBcLZ1KhWipwi1r7jjz0z+d3A02XXb6jHrphl/uAeflliHTvfqNc1t2M9Rrc1NTzEhI8QTbyO39PLWx9uM+Q3z9WkpV1LeznxN8NsOtDqOPY97NjqwP12lt0cwDHENX3P3UZDtnkZ7n5YyVCIFLV+o+bfep8YH/uX753qlbwrfbdQJ7vGOWvWjYObrb2UiJ17cbZg5Z/KIcVtH+buDDxSoB5/df2nP0CQdys4LKYzC4eDiAi98GboFjOdpc/8nSma5uH3XUUM7+A5UeFnv7zlfWs6fq3riwz7ILaHaYqmlM6ufLc4D9f+Ag8QcKbiyGO8TmetX803wve1tKOeh4uDuIVyeFzZ0pZbEHWbh/J1+1HgqOzC9h6kF/FbQXnzqqV43hPwxbwMHIHkYOawi9iYW6OFmIpa0Nz3080CHpUEdQ03PgDhcwDnRhMIBC0l94pW9pW2HfJ7dIlTW8kdR3WHXdYh7KvADTv3ODjDxSMb/GWZLgsrXxZ80ec9uI+4JeiVgJp68g35Vw1bzd4mxHIIyJyKjpQCWoRBvVwXQ2O4zdCcTxe4siHxi0h6q98WLeyhUDWNaGkRc5xWzpRm9BBAOu0nZQ73JQUoKVcEbhF6L6T6eceesY9lMNuHYUEH0gbumxKcNmEohiXVYI5q8fBIi61SGXkkv0pSzh8CKEEXqdrBf9q80MnqmWv0YGHRweijsbBLxBXKyACx8UUgIFcB2+u+aRBG58XN4kpLqdKXXhQu22wkQ0WJBU2PSWwC2p3mKroI3dq5QWdLzzRflIe9WncxC626Eub3Ti7mNimwKKvUqcWvM32HfY8nB1UT7ty0VZzNqQB65/VrW+9H8pmHA95aEvHL51aQI7FrT/HtW1jF7fqgQaX+Gw1cqcqD1dHC7OUtaKLzw8EAAAAAAAAAAAAYgDo+wEA0cN8EeUy5/CHttevJaw334x2EPSPeroF/FkEAAAAXQFURezw/9kXoO8HAATH06ed248IjbxwYCTaJ9lQJ4cUHObmndiJaBpw4WmAwHUBAAAAMQVURezw/9kXoO8HAAAAAAAAAADwD+j7AQAAAAAAAAAA/AP6fgAAAAAAAAAAAP/w0vezCm+G+gftS31XCcvpjfOP3BtkrQyjChkFyRsXBydk1RAQRNFyUUR0wDBFdCEEIaWZB5d5rUxQDn13009DGP+ihJQ+jvbzj7yRWw6rDJ0XEbvZXp3QHfN2F6guEKlGaGsr/l5gfrq2afGq2L/zqwiqw+aFH9g0UYMIIeUZe/39dl7LqSAo9p+2af9ODwMOfx6OAZCK6sTwD1EpJL8LBm4q6BL6gw92vxfXNBcEkoH6kTg1HUx7pjbRU23G2Rqk6S3CYKguSs3ZbV0jRq7BOOKUp51F/GwUq+LDN/i2DteIXyrhDF5zp+O+n/X5mK/HEfnotILpeqz/olzHeoaYv91jktBeuLf/ab/ZFw0SMy5ayTHzj7kPmR4y4HVMPxThntG0q/42waVTRhiT3gjc9kaQ7+f93Q/J7b5X4KD2/VLg9IijmWPXmFcLfd7uAtUv+8aJ6E85oPqcR1lb8fcCKz9u3sxTGrEPPzmrfk1aMcl7ft8nSb5Kt9d47KCtu5HnpUfPDHOy9ww3/XutKSa/PUMqyrYv+FxhI6NNpHGSsKFXMhlmmhf29VQRm3JNmRJfUhPf9KbyfpDVEsjDglx1a5m4uAbjoGY0zhBHG6tuiU3x6QT4tg7HiGMq4Qyec4eHdCIYz4yOG+GhLw1DkKnL5H4hl96VIKYoQob862yCue8QObaM1HuUtf6Py2+KGbIoQmS0rLZPwl0zhRP24UIKEaQw8WDKwJWvJmtKQJC6Y9Sdhj+jQOqEPW/3geqXcb1Ed8Wf1H5tceCF6r+vP9TyfOBQb4HGxJClgw1OJn2ZpXvqImV6oqc+FYKog5cE2EZuPPcqyHQAJo9ORIpjqKGhbPHSeBpHCbtkVDAhGaKM2DT9raFlbF92ediOx8Ola2+IkWswDkpG4w7xs7H2AZ4jHN/W4RrxSyWcwXvudJxNBLWh7jOaXrMKrl97YzzGSoWo1qu9kKw1bqzC4vNXP9k692ZmX0l532/sSBWyDooQhklG5kYQws/ffPIJ/eXTl2q9fux1tzz55AtDZdjcsN2rbHrCMsKet9tA9Ysob/NBW1uceIGFNN1LAkvL9kBy3rwrZLwt1/XRb8oeSX1jjQ/P39IhTB6cYClJYy0IKeYmYZ+LVZYzkfwf62Z9flnEktKUnRagMX0ASbS3jfEMKzd29fG+6x6OlYVZ+W/ExzUYR+zytBOIn42sr3iOcHxbh2vEL5VwBh+5w0c2MT4lBbqE1gUlLutH5CAcvX6Po72bvvpSBcY31uCQ836mJAhGEwofVllJ8dv0R6qXUl6aErOPeI/38Nd5keAm4hvghQGqXzACDrwgNcJ+xMdtYQlu+9w0iu+E7Uurq51aW1lVDVOlqE2bwFJSVGZ1dS37JFukqnYFmNJHdrwlecIMZfOerNenPywP/KicoDNeUdR68UL17fDIQo8T09TYYcWqwp1rAIAWILiOcHxbBwAIDz5yh8cWHClNj5zlGSe7+vJFn35UDkLmq0gX73Sn5Pw1lkrMzymrJ0+bpf7w7JAz7YWJXprCvp8ApkhKKtjO9e4vy57J0DPAdavL9Qy6m52EkOftXlD9giFw4AWChtf+Y7kLV4/RCZQ2mLDQYbxKkaK8jIw0Ul1dA0ENP5pBqiqriTIymPnxGUK/GJgV/Qxhr79ZgPEORzIvp1nq43qvG9f4kmAyTW18wrt7/7HGj8L+fT9IyeX9Z5Vn3TNvCCpYGtOuAQC6CL4jHN/WAQDCg4/c4aXvR8oebnaclTo6Nm3DqJ9XatsLkaI7yZnaU44OUSJCEFF9jLuttN2NjE817YVP6V6aws5kkr6JXm36j2oIauwxEYhIwtzl8K6B6hdsgQsvEDUmbb0yaWv9S2b2Dqs/TZ0Meysayce8eE2HLMlsadXrl/m6/Y0wczIDk+3WG4+k178ky/DU9LM9U5xT9VVG2ki1MZcRBhMmEbEZVG2ovHXhdi+7dTqNcUVQNcayawCALoLvCMe3dQCA8OAjdzru+5GS5BWzTpsdvL9hlDzMTQgrmZj0zLp6+a3vEiMqUp6ZdLtQf4qhCorQoBtu9CHqucwcGLFzc4rNn7byeSd3n68ZE2lBFv683QaqX7AGDryAfD/rbbVbM/bCxmGU7GPBe7+5HrCTkyDNcIVmhMV5x/sa0B7siEgz8dxsiKETGoosmc8Ta+T9+Q8r3ypFbFcbJMd6dbrwJktu7QDMxlUL6C8fPYUGTG++qRGSGI5t1wAAXQPfEY5v6wAA4cF77nTcgdNSj558/5phr7a/SUDUWHQ1cwSKMCtiU8KG5YHOxhEMEsKUNHDcd3SZiZQkipBYddqj9+wLNIjFqGPe1pNaQeg1P+nN7tGCPK0n6i0+FvtlQcAglUKGtNaYJSdjnBXgbpi3u0D1S1aktci6ag5rK+5egJUnBwVd9fHQi6kiKRg5BJ/dbtuDLbbalBCyZKFdn1XlJLWhXgeO++tj9dhUcyPXfn1pHQQx6EiGc+YumDx5tnTK0VYS5yjTlYt1/CPy17sUlbBgBT15350ao2RFrTovMD/lFypoqvwqZFTxcQ3GEas87STiaCO+Ixzf1uEYcUwlnMFz7nTc91NdT1cx24ut0YTQEL+4u35tZPJoQreEUrcOp+4iJM3J25Inb2spku6OebsHDn4RHZzWVuy9IGniHfvIO7aNVGaQ7+FHviJRiD+otjpptm2Faxe031Bqaojh1JDuUEmQSLoklLu0FomNazCOmOVppxBPG/Ed4fi2DreIZyrhDB5zBzwdCwAAAAAAAAAAwD+g7wcAAAAAAAAAAPAP6PsBAAAAAAAAAAD8A/p+AAAAAAAAAAAA/4C+HwAAAAAAAAAAwD+g7wcAAAAAAAAAAPAPL30/q/BmqH/QvtR3lbCc3jj/yL1B1sow89O1TYtXxf6dX0VQHTYv/MCmiRpEiJ53eYP/2rh7edVEecMJy3bF/D5cEYYgpDTz4DKvlQnKoe9u+mkQ6sfksKUQQIqTfS2ckyYkf9g3TqIb5+0OUBYWY/rUJfuoO8ZXkpp0Iw9a//jBGhOWOHkB3YSmx+K2ji5MglRUJ4Z/iEoh+V0wcFNpFDFfnckPiy8rqGJntMLCYI3xfWB0IaapTfRUm3G2Bml6izAYqotSc3Zb12Ts9ffbeS2ngqDYf9qm/Ts9DIT97+C4BWsVRhiIn41IOZ4jHN/W4RrxSyWcwWvudNz3sz4f8/U4Ih+dVjBdj/VflOtYzxDzt3sMj8+beUoj9uEnZ9WvSSsmec/v+yRpHn2fl1fygPgnZ+3VaU/DnGw9N1pkRVnVXPW3CS6dMsKY9ObnmDloW1oLIbuRH8mrgm7DyoRunrcbQErbL6woQdWnrqyUbhX5LrVlEWDl7BEnL6CZ0ETr6MIiSEXZ9gWfK2xktIm0n8KaJ5/WHmfN3dPfQRN5fTRn6boi3cNq6k9RhLqY/sccypT4kpr4pjeV94OslkAeFuSqW8s8dtDW3cjz0qNnhjnZe4ab/r3WFHyxyT9YqzDCQBxtrLq1BscRjm/rcIw4phLO4Dl3eEgngvHM6LgRHvrSMASZukzuF3LpXUnVj+sPtTwfOGhKQJDGxJClgw1OJn3xcTBfGDfS1k6D3cFRBrlOMgxNy61CrCS0fRLumimcsA//FQ0UtC2tKYK+voh8vxK0Ktsz1PNc4NfunLd7IKEsrChB0QcpLy2D5OTlWjfGYuUFdBMaPmkbXViESHEMNTSULV4a/7PvR/69USoxQXdin3qTjNxVhp74kpqrMgBFqKqrj02ntIOWsX3Z5WE7Hg+Xrr1x6iJleqKnPhWCqIOXBNhGbjz3Ksh0AGgc+AdrFUYYiJ+NtQ/wHOH4tg7XiF8q4Qzec6fjbCKoDXWf0fSaVXD92hvjMVYq8Av2G6TpC3ZYWrYHkvMmF1lk5a7RIGFW5CTvPVUwcr61PAwTjMyNIKSo1ZgaI1C27ILBqCDfLq9cneN1JqZf4rnunLebgGXaL6woQdOHVVZSznp31NPij/T8Ghl9W7/tEQHDlcTKC+gmwCjRhUVgKUljLQgpbiFi0fPyWBpOkk2X8ikUbZXa7Lw6ufbCjwgkHn0/Kzd29fG+6x6OlYVZ+W/eluv66DcVNkl9Y40Pz9/SIdA38A/WKowwED8bWV/xHOH4tg7XiF8q4Qw+coePbGJ8Sgp0Ca0LSlzWj0iRsx/xcVtYgts+N43iO2H70upqp9Y2ngZUJEzr7Xm+Rm6gT8xpLx1ud0DwvmVnQL5dXLnmw9yzB0wkshO7cV5AC2BJ/XEe49WnL5tro07L3DPbceoiteenPFRg8fECugnuMKfowj6sGhpEkfy54gRJCkSrYaIIaQj6AFij+nZ4ZKHHiWlq7LBiVVVVw1QpatNHsJQUlVldXQtBVK5DAABiAoLrCMe3dQCA8OAjd3js+5HS9MhZnnGyqy9f9OlXP4qG1/5juQtXj9EJlDaYsNBhvEqRonxj09DD40y5W01h5okVM8bMITw+6d6L0yVD3rfkH+Rr4oqQAt8zB43JELMb5wW0gqA9bdvBaY2vpSwWr/GIdrjysNbDSVJ8vIBmwt8FEuc5RZeoQegXA7Oin7FbdtgswHiHI7ndshLYlYFGY0FQ48V9VjUNokoRUYRUbHqkDUjJ5f1nlWfdM2/4XTUsLSONVFfXQFDD70WQqspqoowMVn87AgDwC74jHN/WAQDCg4/c4aXvR8oebnaclTo6Nm3DKOXmVoCoMWnrlUlb618ys3dY/WnqpFfz8sqZXO3pDv2oBKqaxexFk0Kdk5/WuU9uNzFS8TKJty07TcXtMymFWXfs9CPZb+jlhV8Znsa5KxN2Gv73QajzAlpRV/Qi/ZPcb4M1GwORTmcQycSql1dOCNf7ggTNBPpdlOgKupy83ETEyrKByXbrjUfS61+SZdo3/ey2n6ylRTyVQ2NA0vXZX0PLLaLoaUugCLXEou+vvHXhdi+7dTqNJywEVWMj+ZgXr+mQJZn9tur1y3zd/kYYfdQSAMA3+I5wfFsHAAgPPnKn474fKUleMeu02cH7G0b9ugkb+X7W22q3ZuyFjcMo2ceC935zPWAnT8q4tsXrxefLZ1cPV2bkJf8v5ZvRXEO0CWDSVx637DSy7icL3ZteM19ttbQr2Ja1bxzztr+7cOcFtIKZdWDO1GezL50LHqlYkRETdoZp/9dw6tc/hOx9QYJmwtgZzoUzmz//GV1YOThRZMlcT6HggXYKUHDhJQftKX1Z/x4rytBRWqhFUEURikPfT3/56Ck0YHrzTY2QxPAZrtCMsDjveF8D2oMdEWkmnpsNMf1YIgCAH/Ad4fi2DgAQHrznTsftFi316Mn3rxn2avubBESNRVezIicHBV318dCLqSIpGDkEn91u2wOCbLae3rJixRyTnV9rYSmNoTNij/jpE6tOe/SefYEGsRh1zNt6UisIveYnvYlG21KQK4AOFVVD4c8rFFAXdvdokXWf6I7ecmbb8oA5RuHfmJI9+zusTwx3UpSCxMkL1FEoJohDQ9xAzY1c+/WldRDEoCMZzpm7YLJzlGmQhfq2eR9Dl/wXXQUpmSqv29Sz/ik+ZmhC7MP8lF+ooKnyq5BRrTYlhCxZaNdnVTlJbajXgeP+2A0ubIO1CiMMxNFGfEc4vq3DMeKYSjiD59zpuO+nup6uQruH2cQ79pF3bCsRLGex6NCdRa23o7gllLq13x1lS2FBNAl+8rHxJaqGYoo0+sKKDA76DF5w6N6CQ61lYuUFWBbNhJ+0iC4MQrXVSbNtL4YNpmodmdpGSEATYh5Jl4Ryl9YimUG+hx/5ikYdPIG1CiMMxNNGfEc4vq3DLeKZSjiDx9zB7O0VAAAAAAAAAAAAQGCAvh8AAAAAAAAAAMA/oO8HAAAAAAAAAADwD+j7AQAAAAAAAAAA/AP6fgAAAAAAAAAAAP+Avh8AAAAAAAAAAMA/vPT99LzLG/zXxt3LqybKG05Ytivm9+E/H2COFCf7WjgnTUj+UP+/RazCm6H+QftS31XCcnrj/CP3Blkrw8xP1zYtXhX7d34VQXXYvPADmyZqEOuSfdQd4ytJTU8IJw9a//jBGhOBPqYXfQpCecZef7+d13IqCIr9p23av9PDAJt/E8sTSGnmwWVeKxOUQ9/d9NMQ/ePW0fRBSh9H+/lH3sgth1WGzouI3WyvTkCNExHrzonaRE+1GWdrkKa3CIOhuig1Z/cocuPbVvGPSZCK6sTwD1EpJL8LBm4qrT4qf5DnuaJsWHT/NUNgCGG+OpMfFl9WUMV2isLCYI3xfbDqk5+g1RYIwVWOixasVRhhIH424jvC8W0drhG/VMIdvLmg476flbPPyyt5QPyTs/bqtKdhTraeGy2yoqwbMhH5kbwq6Das3Dg66/MxX48j8tFpBdP1WP9FuY71DDF/u8fw+LyZpzRiH35yVv2atGKS9/y+T5J8FctK6VaR71KFGBt1aFNUpa7x2EFbdyPPS4+eGeZk7xlu+vdaU/H80gMpvepvE1w6ZYQx6Y2odakHVR/k+3l/90Nyu+8VOKh9vxQ4PeJo5thV6ifax8m+cZIi1J0LlCnxJTXxTW8q7wdZLYE8LBqb/jbxj0WQirLtCz5X2MhoE2ltPyori46qgOWb3tY8+bT2OGvunv4OmsjrozlL1xXpHlbTxfQ/5rDy41Bqi9Jt/OS4aMFahREG4mhj1S08Rzi+rcMx4phKOINnF/CQThTzhXEjbe002J0+ZZDrJMPQtNwqxJoCs3u6K0Grsj1DPc8Ffm3YkmA8MzpuhIe+NAxBpi6T+4VceldS9eP6Qy3PBw6aEhCkMTFk6WCDk0lf5jqVlkFy8nJC7JeQcpQpah+cukiZnuipT4Ug6uAlAbaRG8+9CjIdIJ5FhaTtk3DXTOGEfTg20gxFH6Qw8WDKwJWvJte7X90x6o4jW8gqRIkTZFwvzF9dpmVsX3Z52I7Hw6Ub3raLfyxCpDiGGhrKFi+Nb933I4x7UZ8+Tuw98VZBccP7f2+USkzQndjwJ71G7ipDT3xJzVXV1ceyU6r/Rqkts3TxlOOiBWsVRhiIn434Ooq1Bd/W4RrxSyXcwasLOs4mgsYId42GV8yKnOS9pwpGzreWZ3cDyLfLK1fneJ2J6Zd4rmlLtaHuM5r2YhVcv/bGeIyVCvyC/QZpuksClpbtgeS8yaWXlZSz3h31tPgjPb9GRt/Wb3tEwHAlgbYYLJQpLKvfvC3X9dFvMlpS31jjw/O3dEg8awosY2RuBCFFotajGTR96C+fvlTr9WOvu+XJJ18YKsPmhu1eZdMTNU5EoDF/sHJjVx/vu+7hWNkGXdvHPxaBpSSNtSCkuK285F5BTIHSn6sk0241vGfR8/JYGk6STdf3KRRtldrsjwiE6b6/nra15V0hA0c5LlqwVmGEgfjZyPqKp6NYW/BtHa4Rv1TCHTy7gNdsqkiY1tvzfI3cQJ+Y0146BHbXc3Hlmg9zzx4wkchObLsx41NSoEtoXVDisn5Eipz9iI/bwhLc9rlpFN8J25dWVzu1lp3O4zzGq09fNtdGnZa5Z7bj1EVqz095CLL5g1Gm+GdjVTVMlaI2byIlRWVWV9dCEJXrUIBOwz77Kn6b/kj1UspLU2L2Ee/xHv46LxLcmm7mbxknIla0Y6pvh0cWepyYptbU9XOJf6yDlJRGxdQ5hfXVIdemNclYNTSIIvnz2zGCJAWi0RD0/bGC1AiU2lIJchyAZ5AqPEc4vq0DADABr31/D48z5W41hZknVswYM4fwKIq8OqTA98xBYzLEbL0hUpoeOcszTnb15Ys+/epzVcNr/7HchavH6ARKG0xY6DBepUhRnqQ9btvBaY07SFksXuMR7XDlYa2HkwBv8SZoT2s3xeNQS2mkuroGghp/nVBVWU2UkQG/GRIeMEVSUsF2rnd/WXZHaegZ4LrV5XoG3c1Oon2cYBuk5PL+s8qz7pk3/HgX+Zq4gkP8ixyEfjEwK/oZu2WHzQKMdziS255MI4zbkZ+/TtFZpw1DrJ9SAvtQS6Ox3zeegbGqaRCVivGL/QS02iIjA3IcgGNgaTxHOL6tAwAwQYd9P1LxMulMrvZ0h35UAlXNYvaiSaHOyfdv1KUUZt2x049kb0EvL/zK8DTODbqc/Hvv9M2Os1JHx6ZtGPXzAS1EjUlbr0zaWv+Smb3D6k9TJ31W0Yv7n+R+G6zZmNt0OoNIJgn2Zv+6ohfpbacgqxkbyce8eE2HLOt/mFn1+mW+bn8jjD6GBReQ9E30atN/VENQ4yojEJFErP9J6cP2cYJpKm9duN3Lbp1OY1dccfsMavwvNxGtlvXAZLv1xiPp9S/JMu2afjbVFTcf0d9nZk85AdUfV38wGOtefpqjO0uLeCqHxoCk60tCDS23iKKnhXnXtK8thr0VQY4DcAxBFc9HMXxbBwBggg77fpj09doWrxefL59dPVyZkZf8v5RvRnPNpi8v9GzagPlqq6VdwbasfePIJUnzZ502O3h/wyj5nx0D8v2st9VuzdgLG4dRso8F7/3mesBOjvk0ZM7UZ7MvnQseqViRERN2hmn/1zCyQA1jZh1oP4X0cFlXaEZYnHe8rwHtwY6INBPPzYbYv8VEfCHqucwcGLFzc4rNn7byeSd3n68ZE2lBKkle0S5OsA395aOn0IDpzXedyrqfLHRv+uhX/GPl4ESRJXO7PiatEJqi0PSaRYvzyi7y77dmCFz7jwIUXHjJQXtKX9a/x4oydJQWYr3vR60tEqQZIMcBOEZiOJ4jHN/WAQBYoOP7fKg2W09vWbFijsnOr7WwlMbQGbFH/PRR85CWevTk+9cMe7X9TQKixqKrWZGTg4Ku+njoxVSRFIwcgs9ut+0BQaO2nNm2PGCOUfg3pmTP/g7rE8OdFAXbZFBRp4CtNiWELFlo12dVOUltqNeB4/7opogDVac9es++QINYjDrmbT2pFYRe85Pe7B4tsu6Tgz6Lj8V+WRAwSKWQIa01ZsnJGGeF2nOocWIt2BM/gcL8lF+ooKkifr8tq7mRa7++tA6CGHQkwzlzF0x2jjINskDJNYqZ+rZ5H0OX/BddBSmZKq/b1LMPdh9P2gisjFZbIBzluGjBWoURBuJoIxXXEY5v63CMOKYSzuDZBTx0MrCcxaJDdxZx+phoEvzkY+NL19NVaHc7m3jHPvKObT2m7OAFh+4tONTx7J2GwxQyg3wPP/IV4rzdhrRbQqmbqJVoASd9NCdvS568raWEQ5xgGEmXhHIX9I9axD8GodrqpNly/pgg6XOs/883BlO1jkztDq0EhiRKbcFTjosWrFUYYSCeNuI7wvFtHW4Rz1TCFTy7QPyuYAIAAAAAAAAAAAB+AX0/AAAAAAAAAACAf0DfDwAAAAAAAAAA4B/Q9wMAAAAAAAAAAPgH9P0AAAAAAAAAAAD+AX0/AAAAAAAAAACAf3jp++l5lzf4r427l1dNlDecsGxXzO/DFWEIKX0c7ecfeSO3HFYZOi8idrO9OgEpz9jr77fzWk4FQbH/tE37d3oYUCBW4c1Q/6B9qe8qYTm9cf6Re4OslenJPuqO8ZXN/9FLHrT+8YM1JkJ5TC9SnOxr4Zw0IflD/T8roWoopqAtrGj/aQkpzTy4zGtlgnLou5t+GoQmWfs4YRQkb1wcnJBVQ0AQRctFEdEBwwT89w0CpA41VgliE0hIRXVi+IeoFJLfBQM3lQYRi55+OD/qbHl+NSSjKeu+vM/swSQYYb46kx8WX1ZQxQ4nhYXBGuP7YNYnzaAGEp5yXLRgr8IIA7SqhW3wHeH4tg7HAMdhAN6qWcd9Pytnn5dX8oD4J2ft1WlPw5xsPTdaZEVZVZz3dz8kt/tegYPa90uB0yOOZo5dY3xvjccO2robeV569MwwJ3vPcNO/VyvG+3ockY9OK5iux/ovynWsZ4j5232WZaV0q8h3qUIvs8iP5FVBt2HlpmmqbrXXcK2pWH7pwfp8DGVhx0mKTCGk9Kq/TXDplBHGpDe/hN/bx8lqzQS/2RcNEjMuWskx84+5D5keMuD1njGi05w7dWixWpUqHoGEVJRtX/C5wkZGm0j7KfyWlLfmMmnl/gETNJF3J3MXhXw2TuzT/9mntcdZc/f0d9BEXh/NWbquSPewmi6m/zEHKTqBEkhDH4iHazAP5iqMMECtWhgHR0cxFPBtHY4BjhM5PFczHrxCMV8YN9LWToN96kYZ5DrJMDQtt4qln3gwZeDKV5M1JSBI3THqjiN7w9qUUxcp0xM99akQRB28JMA2cuO5V4ELjGdGx43w0JeGIcjUZXK/kEvvSlgmpWWQnLycsK+tIN+vBK3K9gz1PBf4tf597QMUDYNMB4hlbBJQFhYZ10t01+NI2j4Jd80UTtiH/4w5pBAlThgZr7MJ5r5D5NiqknqPstb/cflNMTJGHZtXEpFylFgVn0AiUhxDDQ1li5fG/+r7CdpKK/+QHt+HwF5x3bFyOn+V5ZcjrBulEhN0Jzb8Sa+Ru8rQE19Sc1V19bHplEaY+SiBRGOIi2swD+YqjDBAqVoYR3yKT2fAt3U4BjgOA/BazTp2CkFjhLtGwytmRU7y3lMFI+dbyzNePn2p1uvHXnfLk0++MFSGzQ3bvcqa9uZtua6PftOQkvrGGh+ev2WqubrPaBqKVXD92hvjMVYqSFlJOevdUU+LP9Lza2T0bf22RwQMVxL08QT5dnnl6hyvMzH9Es81zv8VTUM6JJahSVAb2n5hRXlIhmWMzI0gpKiljI4SJzY9jceNVVh8/uonW+fezOwrKe/7jR0pUs25wkKJVctqcQkkWErSWAtCilsJlUwV7Jpff31YnqfVw0ye/iSPpeEk2XR9n0LRVqnN/ohAmO77SSiBpPwtTUxcg3kwV2GEAVrVwja4Ooq1A9/W4RjgOAzAczXj1SkVCdN6e56vkRvoE3PaS4fA+qek+G36I9VLKS9NidlHvMd7+Ov8u6GqGqZKUZtVkJKiMqura9knfw3vGZ+SAl1C64ISl/Ujwu/1x3mMV5++bK6NOi1zz2zHqYvUnp/yEOhBBfl2ceWaD3PPHjCRyE5sElVx1VBMabmwotalLeymuV2cvEhwG71+j6O9m776UgXGN9bgkPN+GP42EJZsH6v/bMRFICFf7xcExSFzdqroEOru0iCK5M8vNQiSFIhGQ0SpHQ9Itw8k4uckPLgGU2C5wvz/A59HsWbwbR2OAY4TJ3jtt3p4nCl3qynMPLFixpg5hMdHpCUlFWzneveXZXcKhp4BrltdrmdSzKSR6uoaCGr4MQdSVVlNlJFpfF2aHjnLM0529eWLPv3q40B72raD0xpHlrJYvMYj2uHKw1oPJ8HdOop8TVwRUuB75qAxGWI2C2FpGU4aiintFhZjwJT2cZJBM33l4p3ulJy/xlKJ+Tll9eRps9QfJnppYvMXdQSUWH0caonZQELoFwOzop+xW3bYLMB4hyMZ/WQaYb488T7kItFrl66jDgFiEdgVm0ZjQVBjZ8eqpkFUKsYv7jJfRbYLpAfReMtx0YL1CvP/D/wdxVqCb+twDHCcONFh349UvEw6k6s93aEflUBVs5i9aFKoc/JT1loTvdr0H9UQJNG4FUQkkVSMjeRjXrymQ5Zktqjq9ct83f5GEhBS9nCz46zU0bFpG0Y1PQ2iruhF+ie53wZrNoYInc4gkkkCbfsqbp9JKcy6Y6cfyX5DLy/8yvA0zg06H4iqoZiCsrBYg6TfPk4IX+8kZ2pPOTpEid1iEtXHuNtK2914SvfSxGaNQItVshp6qGMBmGy33ngkvf4lWYZj0//80Ls/nvT444D6YPkGCYGspUU8lUNjQNL1JaGGlltE0dPCZlA1gxShBNI/ij6YdY3YIQYV5v8fBFXsFp+ug2/rcAxwnDjRYd8Pk75e2+L14vPls6uHKzPykv+X8s1oriFFz2jmwIidm1Ns/rSVzzu5+3zNmEgL6eGSrtCMsDjveF8D2oMdEWkmnpsNCSXJK2adNjt4f8Mo+Z9HDmbWgTlTn82+dC54pGJFRkzYGab9X8PIgrRL1v1koXvzbK+2WtoVbMvaN06i5l57DcX0q2sEbWGxBlHPpV2c/KaqaNIz6+rlt75LjKhIeWbS7UL9KQaYvdEHNValh8tiN5AosmTup1DlDwr+uCG1LlZ9cI+fMnignQIUXHjJQXtKX9a/x4oydJQWYrzvh5VMUAJJargSdl0jVohFhfl/iMTwGTiOcHxbh2OA48SIjtstqs3W01tWrJhjsvNrLSylMXRG7BE/fSIRWnws9suCgEEqhQxprTFLTsY4K8Cw1aaEkCUL7fqsKiepDfU6cNxfn0g7e/Tk+9cMe7X9TeMRNRZdzYrYcmbb8oA5RuHfmJI9+zusTwx36pYHuFNRNOyGaYUBLRVtYSOtBXr6xA9Vpz16z75Ag1iMOuZtPakVhF7zk97sHt0+TiShTQkblgc6G0cwSAhT0sBx39FlwvnvBkFAHYUWq2ihLmpN0ai5kWu/vrQOghh0JMM5cxdMdo4yMb9S/PkDsnTCt6aNCBKu0f2WD1bfNu9j6JL/oqsgJVPldZt69sHmjVe/oFijBRIVEg/XYB7MVRhhwKFqYfo6JY6OYijg2zocAxwncniuZjxcZoXlLBYdurOo3Z6ak7clT97WWigzyPfwI99Wm7mermJC7Rm84NC9BYc6nl0AEE2Cn3xsftNeQzGFymFhRYa0W0KpG4ocJU7kh/jF3fXrHrW6DCyLGqviEUhUW50023ZSC7N0lG1hg6laR6YKXyfBAaMHkni4BvNgrsIIA05VC9vgO8LxbR2OAY4TMTxXM8zeXgEAAAAAAAAAAAAEBuj7AQAAAAAAAAAA/AP6fgAAAAAAAAAAAP+Avh8AAAAAAAAAAMA/oO8HAAAAAAAAAADwD+j7AQAAAAAAAAAA/MND31+X7KPuGF/Z/H+65EHrHz9YY0Ioz9jr77fzWk4FQbH/tE37d3oYUCAERYi6u951tDEF/LRXpPRxtJ9/5I3cclhl6LyI2M326s1PJEeKk30tnJMmJH/YNw7Tj2rmBqvwZqh/0L7Ud5WwnN44/8i9QdYi/lNNpDTz4DKvlQnKoe9u+mkQmmTtvcAoSN64ODghq4aAIIqWiyKiA4Z1y983dAr0+Ic+Xdu0eFXs3/lVBNVh88IPbJqogdGHFSMV1YnhH6JSSH4XDNxU6iX0Bx/sfi+uac59koH6kTg1HZj56kx+WHxZQRU7nBQWBmuM74NZnzSDGkhoVUjUiooraBmNN8TPRnxHOL6twzXil0q4gzcX8NL3l5XSrSLfpbYapCp1jccO2robeV569MwwJ3vPcNO/12rfQRFqoe1eiSYULMj38/7uh+R23ytwUPt+KXB6xNHMsWssGpp85EfyqqDbsLJYxyXr8zFfjyPy0WkF0/VY/0W5jvUMMX+7b5ykyBRCSq/62wSXThlhTHrzS4jihdWaCX6zLxokZly0kmPmH3MfMj1kwOs9Y0SnOXfQ4p+Vf3DezFMasQ8/Oat+TVoxyXt+3ydJvhj8oyukomz7gs8VNjLaRNpPIb2SyTDTvLCvp0oLhWvSP609zpq7p7+DJvL6aM7SdUW6h9V0MXou0whSdAIlkIY+QKlCpuCLTf5BzWicIY42Vt3Cc4Tj2zocI46phDN4dkHH6YSUl5ZBcvJyrXqa2genLlKmJ3rqUyGIOnhJgG3kxnOvAoahCFfOR9kddUzBghQmHkwZuPLVZE12q6/uGHXH8ecn368Ercr2DPU8F/hVePMLH4LxzOi4ER760jAEmbpM7hdy6V0JMq6X6K7RkrR9Eu6aKZywD/8Zc6heYGS8ziaY+w6RY6tK6j3KWv/H5TfFyBh1bF5dRo3V6r+vP9TyfOBQb5bGxJClgw1OJn2Zt6g39hp/IsUx1NBQtnhp/K++v6qCCckQZVqn5L83SiUm6E5sOHcxclcZeuJLaq6qrj42ndIIMx8lkGgMlCoUZDoANA78g5LRuEP8bEQ9+OImwvFtHa4Rv1TCHby6oONsYpWVlLPeHfW0+CM9v0ZG39Zve0SAZfWbt+W6PvpNe0vqG2t8eP7ms2J74dtalN2Hy6MJlQTaYtBfPn2p1uvHXnfLk0++MFSGzQ3bvcqmJwwh3y6vXJ3jdSamX+I5Qc7X7RDUhrrPaHrNKrh+7Y3xGCsVUXZpsIyRuRGEFLWUoXvBeNxYhcXnr36yde7NzL6S8r7f2JEi1ZwraPE/vP57ZxaCNG4BS8v2QHLe5DIh7PX9sJSksRaEFLeUIZXlTCT/x7pZn18WsaQ0ZacFaEw3ZeXlsTScJJuu71Mo2iq12R8RCNN9PwklkJS/paFUIToE+gb+QctovCF+NrK+ohx8cRPh+LYO14hfKuEOnl3QcTbBkvrjPMarT18210adlrlntuPURWr/bKyqhqlS1OZNpKSozOqqUhRhdR3K7s9PDkURnvIQZPPHbteK36Y/Ur2U8tKUmH3Ee7yHv86LhGnIxZVrPsw9e8BEIjtRcJOJFManpECX0LqgxGX9MHdXBroX3Eav3+No76avvlSB8Y01OOS8H4a/xkWL/+cnR9qP+LgtLMFtn5tG8Z2wfWl1tVNrEVGryiMwpY/seEvyhBnK5j1Zr09/WB74UfmEeg0Nokj+PG8hSFIgGg3rFkm3DyTi5ySUKlQLQVSuIwEAYgJShXacxUuE49s6AAATdNxvEbSnbTs4rfG1lMXiNR7RDlceh1pKI9XVNRDU8IMbpKqymijTQ16mvVCGqj213e4P6R7tx3xY6+EkwFu8YYqkpILtXO/+suxextAzwHWry/Unn0knQwp8zxw0JkNMwU0lQpDS9MhZnnGyqy9f9OmHwcqI5oUMmukrF+90p+T8NZZKzM8pqydPm6X+MNFLE3MXyxtAi392AHvtP5a7cPUYnUBpgwkLHcarFCnKY0N/hH4xMCv6Gbtlh80CjHc4ktufTKuP671uXONLgsk0tfEJ7+69UO9PZTf6LAhqPHdkVdMgKhXLF/vZMF9FtgukB9FoVQj8LhCAF2BpPEc4vq0DADBBx31/XdGL9E9yvw3WbMxDOp1BJJPVjI3kY168pkOWZLaw6vXLfN3+xhooQiOo6MX9truTGGhCwbZNJH0Tvdr0H9UQ1Pi8HgQikurSzqQUZt2x049kC+jlhV8Znsa5QZeTlwv6SULdA1L2cLPjrNTRsWkbRon4QT6cQPMC4eud5EztKUeHKLFXnag+xt1W2u7GU7qXJjaLO1r8s2OVqDFp65VJW+tlzOwdVn+aOulj4zsLmGy33ngkvf4lWQal6a9/mFVO1VcZaSPVhg8RhMGESSQJLS3iqRwaA5KuN6OGlltE0dPCZlA1gxShBNI/ij4oVUhsn9kFALSBoIp2nMVLhOPbOgAAE3TcqzCzDsyZ+mz2pXPBIxUrMmLCzjDt/xomPVzWFZoRFucd72tAe7AjIs3Ec7MhVWNGeyGU9Xv73QlZG9oLyQI1jKjnMnNgxM7NKTZ/2srnndx9vmZMpPWMKYUzm816tdXSrmBbltg+xxMpSV4x67TZwfsbRsljtj9D88JvqoomPbOuXn7ru8SIipRnJt0u1J9igI2mGQXU+Cd9P+tltVsz9sLGYZTsY8F7v7kesJMTtabNUGTJXE+hkPfnP6x8qxSxXW2QHOvV6cKbLLm1AwgDpRWg4MJLDtpT+rL+PVaUoaO0EON9P6xkghJIUsOV2lchsTyvBwDQkBiOcpzFTYTj2zoAAAt03G5RR205s215wByj8G9MyZ79HdYnhjspwrDVpoSQJQvt+qwqJ6kN9Tpw3F+fnZsoQpIeyu5SENqYgrWMqLf4WOyXBQGDVAoZ0lpjlpyMcVbAdh/DH7TUoyffv2bYq+1vEhA1Fl3NirQW7OkTH1Sd9ug9+wINYjHqmLf1pFYQes1PerN7dHsvSEKbEjYsD3Q2jmCQEKakgeO+o8uw+40LavwT4MlBQVd9PPRiqkgKRg7BZ7fb9hC1oqjU3Mi1X19aB0EMOpLhnLkLJjtHma5crOMfkb/epaiEBSvoyfvu1BglC8Fm6tvmfQxd8l90FaRkqrxuU08MPpa0NRRrtECiQmilCcA/HDJaTC+UoCOONlJRD754Ad/W4RhxTCWcwbMLeLjMCssOXnDo3oJDbcQyg3wPP/LtWIi+O/qYgoWkOXlb8uRt6B8STYKffBTq9EKG6nq6ClM/UpB2Syh1Q5GjeEF+iF/cXb/uUavLoAewpIl37CPvWNGoxDtUW5002/ZiqakhhlND2ggJBlO1jkztFrUEBIweSKilCcA3nDIaT4injfiOcHxbh1vEM5VwBc8uwOztFQAAAAAAAAAAAEBggL4fAAAAAAAAAADAP6DvBwAAAAAAAAAA8A/o+wEAAAAAAAAAAPwD+n4AAAAAAAAAAAD/gL4fAAAAAAAAAADAPzz1/Ujp42g//8gbueWwytB5EbGb7dUJaEJGso+6Y3xl8z/vkgetf/xg+Zs5ajPO1iDNQzEYqotSc3aPIiOlmQeXea1MUA59d9NPQxiPCudRwzXYfXY8d1iFN0P9g/alvquE5fTG+UfuDbIW8d/2ovkULXiQ8oy9/n47r+VUEBT7T9u0f6eHATb/rLeeOtSYgT5d27R4Vezf+VUE1WHzwg9smqiB0TBCKqoTwz9EpZD8Lhi4qTSIWPT0w/lRZ8vzqyEZTVn35X1mDybBCPPVmfyw+LKCKnY4KSwM1hjfB/P/d8EoSN64ODghq4aAIIqWiyKiA4YpwmIVXRhH+FVa9IifjfiOcHxbh2OA40QOry7goe9Hvp/3dz8kt/tegYPa90uB0yOOZo5dY16OIjQqK6VbRb5LbVU8TeJLauKbXlfeD7JaAnlYsJv+q/42waVTRhiT3gjAWp7VRtVQPGF9PubrcUQ+Oq1guh7rvyjXsZ4h5m/3jZMUmUKoPkX1gvG9NR47aOtu5Hnp0TPDnOw9w03/XmuK1a+e6lBihpV/cN7MUxqxDz85q35NWjHJe37fJ0m+GPyjK6SibPuCzxU2MtpE2k/ht6S8NZdJK/cPmKCJvDuZuyjks3Fin/7PPq09zpq7p7+DJvL6aM7SdUW6h9V0MXou0whSdMJv9kWDxIyLVnLM/GPuQ6aHDHi9Z+gDcYouLNMNVVrkiKONVbfwHOH4tg7HAMeJHJ5d0LFXkMLEgykDV76arCkBQeqOUXcc64Vf0ISfS8sgOXk5Tt0PLWP7ssvDdjweLs0+A9D2SbhrpnDCPlxI1RZd7Q40FCsIxjOj40Z46EvDEGTqMrlfyKV3Jci4XqK7Rktq71NUL9SmnLpImZ7oqU+FIOrgJQG2kRvPvQoyHYDNCoGUo8RM9d/XH2p5PnCoN0tjYsjSwQYnk77MW9Qbe4FFpDiGGhrKFi+N/9X3E7SVVv4hPb4PgR0rumPldP4qyy9HWDdKJSboTmw4dzFyVxl64ktqrqquPpYv+TPzX2cTzH2HyLGVJPUeZa3/4/KbYhpDnKIL26BkNO4QPxtrH+A5wvFtHY4BjhM5vLugY6fQXz59qdbrx153y5NPvjBUhs0N273KRg5NqFhWUs56d9TT4o/0/BoZfVu/7REBw5WaGwdWbuzq433XPRwrWy+RMTI3gpAiwZrdodrcNRQvCGpD3Wc0vWYVXL/2xniMlYooTYFRfIrmBWvam7fluj76TaEnqW+s8eH5WzqE0QLBQouZ+u/OWEjTzWuwtGwPJOdNLhPCXt8PS0kaa0FIcSuhkqmCXfPrrw/L87R6mMnTn+SxNJwkm67vUyjaKrXZHxEI030/yXjcWIXF569+snXuzcy+kvK+39iRyt/SxCm6MA1aRuMN8bOR9VWs6ief4Ns6HAMcJ3L4cEHHTmH3PcVv0x+pXkp5aUrMPuI93sNf58URIorwxG/64zzGq09fNtdGnZa5Z7bj1EVqz095NDaj1bfDIws9TkxT66ZGAlVtrhqKK4xPSYEuoXVBicv6Ye6uDDQv/LuhqhqmSlGbNoGlpKjM6upa9hmqSFXlBCyJEjMnR9qP+LgtLMFtn5tG8Z2wfWl1tVNrkY4HwxbI1/sFQXHInJ0qOoS6uzSIIvnzvIUgSYFoNKxbJD16/R5Hezd99aUKjG+swSHn/UyJn5PEKboAAD5BqsSqfvIJvq3DMcBxIocPF3Tc98MUSUkF27ne/WXZTYGhZ4DrVpfrGYwpKEKm27RtB6c17iVlsXiNR7TDlYe1Hk6SbI1KLu8/qzzrnrmEAM3kX20uGoonSGl65CzPONnVly/69MNggqF5IZNiJo1UV9dAUMMvTpCqymqijAxmfwBE0EaJGbqH1/5juQtXj9EJlDaYsNBhvEqRojw2LvYj9IuBWdHP2C07bBZgvMORjH5SizBfnngfcpHotUvXUYcAsQjsckGjsSCo8dyRVU2DqFSMnw8zX0W6eKc7JeevsVRifk5ZPXnaLPUH0TLiFF0AAJ/A0niOcHxbh2OA40QOHy7ouO8n6Zvo1ab/qIagxp4dgYgkIqqwruhF+ie53wZrNs5KpzOI5KanoFTeunC7l906ne67IM2vhmIIUvZws+Os1NGxaRtGifhBPpxA8wJJxdhIPubFazpkSWaLql6/zNftb9RtJ4T8wiFmiBqTtl6ZtLVexszeYfWnqZM+Nr7QhMl2641H0utfkmU4Nv3PD73740mPPw6oD5ZvkBDIWlrEUzk0BiRdb0YNLbeIoqeFzaBqBim6k5ypPeXoECV2WSGqj3G3lba78Y+ijzhFFwDAJwRVsaqffIJv63AMcJzI4cMFHfcqRD2XmQMjdm5OsfnTVj7v5O7zNWMiLST1tNsLCVnr50x9NvvSueCRihUZMWFnmPZ/DatXAKK/fPQUGjC9OzsjVLU5ayh+ICXJK2adNjt4f8Moecz2Z6hekB4u6QrNCIvzjvc1oD3YEZFm4rnZEHO3KDXDzDrQPmZI3896We3WjL2wcRgl+1jw3m+uB+zkRK1pMxRZMvfLLOUPCv64IbUuVn1wj58yeKCdAhRceMlBe0pf1r/HijJ0lBZivO+HlUxMemZdvfzWd4kRFSnPTLpdqD/FQGq4khhFFwDALxLDZ+A4wvFtHY4BjhM5vLuAh06cqLf4WOyXBQGDVAoZ0lpjlpyMcVaAYYX2Qiloy5ltywPmGIV/Y0r27O+wPjHcSbGhdWB+yi9U0FT5NVnVaY/esy/QIBajjnlbT2oFodf8pDe7Rwvy7BBNbc4aih+01KMn379m2KvtbxIQNRZdzYq0FtlpDAefogWP1aaEkCUL7fqsKiepDfU6cNxfH7v1gToKJWYI8OSgoKs+HnoxVSQFI4fgs9tte3Q8lAiouZFrv760DoIYdCTDOXMXTHaOMjG/Uvz5A7J0wremjQgSrtH9lg9W3zbvY+iS/6KrICVT5XWbemLwsaStoVhvStiwPNDZOIJBQpiSBo77ji4zIVIhMYouTNMNVVrkiKONVHGqn3yDb+twDHCcyOHZBTxdgSdpTt6WPHlbx0LZwQsO3VtwqN0Aki4J5S4tBdJuCaVuvEzdFfjRUPygup6uYopaiZZw8ila8MgM8j38yLdb1OoyMGrMSJp4xz7yjhWNSrxDtdVJs20ntTBLR9kWNpiqdWSq8HUSHLD8EL+4u35txeIUXVimW6q0iBFPG/Ed4fi2DscAx4kcHl2AjXuSAQAAAAAAAAAAgDABfT8AAAAAAAAAAIB/QN8PAAAAAAAAAADgH9D3AwCCw9xc1BoAAAAAAAAAoAP6fgAAAAAAAAAAAP+Avh8AAAAAAAAAAMA/oO8HAAAAAAAAAADwD+j7AQAAAAAAAAAA/AP6fgAAAAAAAAAAAP/8H1AcnzH7p3nlAAAAAElFTkSuQmCC)

# In[ ]:


# Start importing the required libraries
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

# Pretty display for notebooks
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


# Upload data file into dataframe df
df = pd.read_csv("../input/cardio-data-dv13032020/cardiovascular_diseases_dv3.csv", sep=';')

df.info()
df.head()


# In[ ]:


print(format(df.duplicated().sum())) # 3820 duplicates???


# In[ ]:


# Explore duplicates
duplicated = df[df.duplicated(keep=False)]
duplicated = duplicated.sort_values(by=['AGE', 'GENDER', 'HEIGHT'], ascending= False) 
# I sorted the values to see duplication clearly

duplicated.head(6) # Show 3 duplicate pairs


# In[ ]:


# Drop duplicates
df.drop_duplicates(inplace=True)
print(format(df.duplicated().sum())) # now 0 duplicates???


# In[ ]:


df.describe() # There are no negative values, nore ridiculous out of scale values


# In[ ]:


# Distributions of age, height and weight variables
fig, axes = plt.subplots(1,3, figsize=(18,4))
sns.distplot(df.AGE, bins=10, kde=True, ax=axes[0])
sns.distplot(df.HEIGHT, bins=10, kde=True, ax=axes[1])
sns.distplot(df.WEIGHT, bins=10, kde=True, ax=axes[2])


# In[ ]:


correlation = df.corr()

plt.figure(figsize=(12, 10))
heatmap = sns.heatmap(correlation, annot=True, linewidths=0, vmin=-1, cmap="RdBu_r")


# The most influential variables in having CARDIO_DISEASE are AGE, WEIGHT, CHOLESTEROL and primarily AP_HIGH and AP_LOW.

# ## Preparation of data for training models
# The data set is first split into X (features) and y (target variable) components, and then randomly into train and test sub sets. 

# In[ ]:


# Import train_test_split and divide data into X and y components
from sklearn.model_selection import train_test_split

y = df['CARDIO_DISEASE']
X = df.drop(['CARDIO_DISEASE'], axis=1, inplace=False)
X.head()


# In[ ]:


# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y,                                
                                                    test_size = 0.25, 
                                                    random_state = 0)

# Show the results of the split
print("Training set has {} samples.".format(X_train.shape[0]))
print("Testing set has {} samples.".format(X_test.shape[0]))


# ## Decission Tree predictor

# In[ ]:


# Import DecissionTree classification model from sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

DT_predictor = DecisionTreeClassifier(max_depth=3, min_samples_split=50, min_samples_leaf=50, random_state=13)
DT_predictor.fit(X_train, y_train)
y_predicted = DT_predictor.predict(X_test)
y_predicted


# In[ ]:


# Evaluate the model
print("------------------------------------------------------") 
print("Confussion Matrix")
print("------------------------------------------------------")
print(confusion_matrix(y_test,y_predicted))
print("------------------------------------------------------")
print("Classification Report")
print("------------------------------------------------------")
print(classification_report(y_test,y_predicted))
print("------------------------------------------------------")
DT_accuracy = round(accuracy_score(y_test, y_predicted), 2)
print("Overall accuracy score: " + str(DT_accuracy))
print("------------------------------------------------------")


# In[ ]:


# Install pydotplus package into the kernel
get_ipython().system('pip install pydotplus')


# In[ ]:


# Plot the Decission Tree model created with X_train, y_train
from sklearn.externals.six import StringIO  
from IPython.display import Image  
from sklearn.tree import export_graphviz
import pydotplus as pydot

dot_data = StringIO()

export_graphviz(DT_predictor, out_file=dot_data,  
                filled=True, rounded=True,
                feature_names=X.columns,
                class_names=True,
                rotate=True)

graph = pydot.graph_from_dot_data(dot_data.getvalue())  
Image(graph.create_png())


# ## Random Forest predictor

# In[ ]:


# Import Random Forest classification model from sklearn
from sklearn.ensemble import RandomForestClassifier

RF_predictor = RandomForestClassifier(n_estimators=50, random_state=17)
RF_predictor.fit(X_train, y_train)
y_predicted = RF_predictor.predict(X_test)
y_predicted


# In[ ]:


# Evaluate the model
print("------------------------------------------------------") 
print("Confussion Matrix")
print("------------------------------------------------------")
print(confusion_matrix(y_test,y_predicted))
print("------------------------------------------------------")
print("Classification Report")
print("------------------------------------------------------")
print(classification_report(y_test,y_predicted))
print("------------------------------------------------------")
RF_accuracy = round(accuracy_score(y_test, y_predicted), 2)
print("Overall accuracy score: " + str(RF_accuracy))
print("------------------------------------------------------")


# ## Support Vector Machine (SVM) predictor

# In[ ]:


# Feature Scaling, required by SVM and KNN algorithms
from sklearn.preprocessing import StandardScaler

sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Import SVM classification model from sklearn
from sklearn.svm import SVC

SV_classifier = SVC(kernel='linear')
SV_classifier.fit(X_train, y_train)
y_predicted = SV_classifier.predict(X_test)
y_predicted


# In[ ]:


# Evaluate the model
print("------------------------------------------------------") 
print("Confussion Matrix")
print("------------------------------------------------------")
print(confusion_matrix(y_test,y_predicted))
print("------------------------------------------------------")
print("Classification Report")
print("------------------------------------------------------")
print(classification_report(y_test,y_predicted))
print("------------------------------------------------------")
SV_accuracy = round(accuracy_score(y_test, y_predicted), 2)
print("Overall accuracy score: " + str(SV_accuracy))
print("------------------------------------------------------")


# ## K Nearest Neighbors predictor

# In[ ]:


# Feature Scaling also needed, but already performed


# In[ ]:


# Import KNN classification model from sklearn
from sklearn.neighbors import KNeighborsClassifier

KNN_classifier = KNeighborsClassifier(n_neighbors=25)
KNN_classifier.fit(X_train, y_train)
y_predicted = KNN_classifier.predict(X_test)
y_predicted


# In[ ]:


# Evaluate the model
print("------------------------------------------------------") 
print("Confussion Matrix")
print("------------------------------------------------------")
print(confusion_matrix(y_test,y_predicted))
print("------------------------------------------------------")
print("Classification Report")
print("------------------------------------------------------")
print(classification_report(y_test,y_predicted))
print("------------------------------------------------------")
KNN_accuracy = round(accuracy_score(y_test, y_predicted), 2)
print("Overall accuracy score: " + str(KNN_accuracy))
print("------------------------------------------------------")


# In[ ]:


# Compare accuracy of the four classification models
compare_scores = {'Decission Tree': DT_accuracy, 'Random Forest': RF_accuracy, 'Support Vector Machine (SVM)': SV_accuracy, 'K Nearest Neighbors (KNN)': KNN_accuracy}
compare_scores


# End of notebook